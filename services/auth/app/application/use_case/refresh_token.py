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
    now = int(time.time())
    access_token = generate_token()
    new_refresh_token = generate_token()
    session_id = generate_token()

    access_token_ttl = int(config.get("ACCESS_TOKEN_TTL"))
    refresh_token_ttl = int(config.get("REFRESH_TOKEN_TTL"))

    matched_user_id = None
    redis_key = None

    # Search for matching refresh token
    pattern = f"user:tokens:*:{device_id}"
    keys = await keyvalue_adapter._client.keys(pattern)
    for key in keys:
        data = await keyvalue_adapter.get_token(key)
        if not data:
            continue
        try:
            token_data = json.loads(data)
            if token_data.get("refresh_token") == refresh_token:
                redis_key = key.decode() if isinstance(key, bytes) else key
                matched_user_id = redis_key.split(":")[2]
                break
        except Exception as e:
            logger.warning("Malformed token JSON in Redis key %s: %s", key, e)

    if not matched_user_id:
        logger.warning("Refresh token not found or invalid for device: %s", device_id)
        return AuthResponse(
            user=None,
            tokens=None,
            error="Invalid refresh token",
            status_code=401
        )

    user = database_adapter.get_user_by_id(matched_user_id)
    if not user:
        logger.warning("No user found with ID: %s", matched_user_id)
        return AuthResponse(
            user=None,
            tokens=None,
            error="User not found",
            status_code=401
        )

    new_token_obj = UserToken(
        access_token=access_token,
        refresh_token=new_refresh_token,
        issued_at=now,
        expires_at=now + access_token_ttl,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        session_id=session_id
    )

    new_redis_value = json.dumps(new_token_obj.__dict__)
    await keyvalue_adapter.set_token(redis_key, new_redis_value, ex=access_token_ttl)

    logger.info("Refreshed tokens for user %s with key %s", matched_user_id, redis_key)

    return AuthResponse(
        user={
            "id": user.id,
            "email": user.email,
            "name": getattr(user, "name", None)
        },
        tokens={
            "access_token": access_token,
            "refresh_token": new_refresh_token
        },
        error=None,
        status_code=200
    )
