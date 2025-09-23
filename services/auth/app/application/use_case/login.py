import json
import time
import logging
from app.common.utility import verify_password, generate_token
from app.application.use_case.auth_response import AuthResponse
from app.interfaces.keyvalue.token_data_object import UserToken
from app.common.config import Config

logger = logging.getLogger(__name__)

async def login(
    config: Config,
    email: str,
    password: str,
    ip_address: str,
    user_agent: str,
    device_id: str,
    database_adapter,
    keyvalue_adapter,
    AuthResponse
):
    try:
        user = database_adapter.get_user_by_email(email)
    except Exception as e:
        logger.error("Database error while fetching user: %s", str(e))
        return AuthResponse(
            user=None,
            tokens=None,
            error="Database unavailable. Please try again later.",
            status_code=503
        )
    
    if not user:
        logger.info("User not found for email: %s", email)
        return AuthResponse(
            user=None,
            tokens=None,
            error="Invalid email or password",
            status_code=401
        )
    
    if not verify_password(password, user.hashed_password):
        logger.info("Invalid password for email: %s", email)
        return AuthResponse(
            user=None,
            tokens=None,
            error="Invalid email or password",
            status_code=401
        )

    now = int(time.time())
    access_token = generate_token()
    refresh_token = generate_token()
    session_id = generate_token()

    access_token_ttl = int(config.get("ACCESS_TOKEN_TTL"))
    refresh_token_ttl = int(config.get("REFRESH_TOKEN_TTL"))

    access_token_obj = UserToken(
        access_token=access_token,
        refresh_token=refresh_token,
        issued_at=now,
        expires_at=now + access_token_ttl,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        session_id=session_id
    )

    redis_key = f"user:tokens:{str(user.id)}:{device_id}"
    redis_value = json.dumps(access_token_obj.__dict__)

    await keyvalue_adapter.set_token(redis_key, redis_value, ex=refresh_token_ttl)

    # FIXED: Also store refresh token as direct key for reverse lookup during refresh
    refresh_lookup_data = {
        "user_id": str(user.id),  # Convert UUID to string for JSON serialization
        "device_id": device_id,
        "redis_key": redis_key  # So we can find the full token data
    }
    refresh_lookup_value = json.dumps(refresh_lookup_data)
    await keyvalue_adapter.set_token(refresh_token, refresh_lookup_value, ex=refresh_token_ttl)

    stored_value = await keyvalue_adapter.get_token(redis_key)
    logger.info("Stored token in Redis: key=%s, value=%s", redis_key, stored_value)
    logger.info("Stored refresh lookup: token=%s..., data=%s", refresh_token[:20], refresh_lookup_value)

    return AuthResponse(
        user={
            "id": str(user.id),  # Convert UUID to string for JSON serialization
            "email": user.email,
            "name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        },
        tokens={
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        error=None,
        status_code=200
    )
