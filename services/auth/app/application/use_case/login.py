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
    user = database_adapter.get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
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

    redis_key = f"user:tokens:{user.id}:{device_id}"
    redis_value = json.dumps(access_token_obj.__dict__)

    await keyvalue_adapter.set_token(redis_key, redis_value, ex=access_token_ttl)

    stored_value = await keyvalue_adapter.get_token(redis_key)
    logger.info("Stored token in Redis: key=%s, value=%s", redis_key, stored_value)

    return AuthResponse(
        user={
            "id": user.id,
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
