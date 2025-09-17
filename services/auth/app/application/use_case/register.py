import json
import time
import logging
from app.common.utility import generate_token, hash_password
from app.application.use_case.auth_response import AuthResponse
from app.interfaces.keyvalue.token_data_object import UserToken
from app.common.config import Config

logger = logging.getLogger(__name__)

async def register(
    config: Config,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    ip_address: str,
    user_agent: str,
    device_id: str,
    database_adapter,
    keyvalue_adapter,
    AuthResponse
):
    existing_user = database_adapter.get_user_by_email(email)
    if existing_user:
        return AuthResponse(
            user=None,
            tokens=None,
            error="Email already registered",
            status_code=400
        )

    password_hash = hash_password(password)
    try:
        new_user = database_adapter.create_user(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
    except Exception as e:
        logger.error("Failed to create user: %s", str(e))
        return AuthResponse(
            user=None,
            tokens=None,
            error="Failed to create user",
            status_code=500
        )

    now = int(time.time())
    access_token = generate_token()
    refresh_token = generate_token()
    session_id = generate_token()

    access_token_ttl = int(config.get("ACCESS_TOKEN_TTL"))
    refresh_token_ttl = int(config.get("REFRESH_TOKEN_TTL"))

    token_data = UserToken(
        access_token=access_token,
        refresh_token=refresh_token,
        issued_at=now,
        expires_at=now + access_token_ttl,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        session_id=session_id
    )

    redis_key = f"user:tokens:{new_user.id}:{device_id}"
    redis_value = json.dumps(token_data.__dict__)
    await keyvalue_adapter.set_token(redis_key, redis_value, ex=access_token_ttl)

    stored = await keyvalue_adapter.get_token(redis_key)
    logger.info("Stored new user token in Redis: key=%s, value=%s", redis_key, stored)

    return AuthResponse(
        user={
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name
        },
        tokens={
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        error=None,
        status_code=200
    )
