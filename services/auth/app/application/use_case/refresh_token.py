import json
import time
import logging
from app.common.utility import generate_token
from app.application.use_case.auth_response import AuthResponse
from app.interfaces.keyvalue.token_data_object import UserToken
from app.common.config import Config

logger = logging.getLogger(__name__)

async def refresh(
    config: Config,
    refresh_token: str,
    ip_address: str,
    user_agent: str,
    device_id: str,
    database_adapter,
    keyvalue_adapter,
    AuthResponse
):
    logger.info(f"Starting refresh for token: {refresh_token[:20]}... device: {device_id}")
    
    try:
        # FIXED: Use refresh token as direct key to get lookup data
        logger.info("Looking up refresh token in Redis...")
        
        refresh_lookup_json = await keyvalue_adapter.get_token(refresh_token)
        
        if not refresh_lookup_json:
            logger.warning(f"Refresh token not found in Redis: {refresh_token[:20]}...")
            raise Exception("Invalid refresh token")
        
        # Parse the lookup data
        try:
            refresh_lookup = json.loads(refresh_lookup_json)
            user_id = refresh_lookup["user_id"]
            stored_device_id = refresh_lookup["device_id"]
            redis_key = refresh_lookup["redis_key"]
            logger.info(f"Found refresh lookup: user_id={user_id}, device_id={stored_device_id}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse refresh lookup data: {e}")
            raise Exception("Invalid refresh token")
        
        # Validate device ID matches
        if stored_device_id != device_id:
            logger.warning(f"Device ID mismatch. Stored: {stored_device_id}, Provided: {device_id}")
            raise Exception("Invalid refresh token")
        
        # Get the full token data
        stored_token_json = await keyvalue_adapter.get_token(redis_key)
        if not stored_token_json:
            logger.warning(f"Token data not found for key: {redis_key}")
            raise Exception("Invalid refresh token")
        
        try:
            stored_token_dict = json.loads(stored_token_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse stored token data: {e}")
            raise Exception("Invalid refresh token")
        
        # Verify the refresh token matches
        if stored_token_dict.get("refresh_token") != refresh_token:
            logger.warning("Refresh token mismatch in stored data")
            raise Exception("Invalid refresh token")
        
        # Check if token is expired
        now = int(time.time())
        expires_at = stored_token_dict.get("expires_at", 0)
        if expires_at < now:
            logger.warning(f"Refresh token expired. Expires: {expires_at}, Now: {now}")
            # Clean up expired tokens
            await keyvalue_adapter.delete_token(refresh_token)
            await keyvalue_adapter.delete_token(redis_key)
            raise Exception("Refresh token expired")
        
        logger.info("Refresh token validation passed, generating new tokens...")
        
        # Generate new tokens
        new_access_token = generate_token()
        new_refresh_token = generate_token()
        new_session_id = generate_token()
        
        # Get TTL values from config
        try:
            access_token_ttl = int(config.get("ACCESS_TOKEN_TTL"))
        except KeyError:
            access_token_ttl = 3600  # 1 hour default
            
        try:
            refresh_token_ttl = int(config.get("REFRESH_TOKEN_TTL"))
        except KeyError:
            refresh_token_ttl = 604800  # 7 days default
        
        # Create new token data object matching the login pattern
        new_token_data = UserToken(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            issued_at=now,
            expires_at=now + refresh_token_ttl,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            session_id=new_session_id
        )
        
        # Store new token data using the same pattern as login
        new_redis_key = f"user:tokens:{user_id}:{device_id}"
        new_redis_value = json.dumps(new_token_data.__dict__)
        
        # Store new token data
        await keyvalue_adapter.set_token(new_redis_key, new_redis_value, ex=refresh_token_ttl)
        
        # Store new refresh token lookup
        new_refresh_lookup = {
            "user_id": user_id,
            "device_id": device_id,
            "redis_key": new_redis_key
        }
        new_refresh_lookup_value = json.dumps(new_refresh_lookup)
        await keyvalue_adapter.set_token(new_refresh_token, new_refresh_lookup_value, ex=refresh_token_ttl)
        
        # Clean up old tokens
        await keyvalue_adapter.delete_token(refresh_token)  # Remove old refresh lookup
        # NOTE: Don't delete redis_key since new_redis_key is the same for same user/device
        # The new token data already overwrote the old token data at the same key
        logger.info("FIXED: Only deleting old refresh token, not main token data")
        
        logger.info("New tokens generated and stored successfully")
        
        # Get user data from database
        user = database_adapter.get_user_by_id(user_id)
        if not user:
            logger.error(f"User not found in database: {user_id}")
            raise Exception("User not found")
        
        # Create response
        tokens = {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": access_token_ttl
        }
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        }
        
        auth_response = AuthResponse(
            user=user_data,
            tokens=tokens,
            error=None,
            status_code=200
        )
        
        logger.info(f"Refresh completed successfully for user: {user.id}")
        return auth_response
        
    except Exception as e:
        logger.error(f"Refresh failed for device {device_id}: {str(e)}")
        raise e
