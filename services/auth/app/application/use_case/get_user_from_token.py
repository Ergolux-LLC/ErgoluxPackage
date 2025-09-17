import json
import logging
import time
from app.application.use_case.auth_response import AuthResponse
from app.common.config import Config
from app.interfaces.keyvalue.token_data_object import UserToken

logger = logging.getLogger(__name__)

async def get_user_from_token(
    access_token: str,
    ip_address: str,
    user_agent: str,
    device_id: str,
    database_adapter,
    keyvalue_adapter,
    config: Config
):
    logger.debug("get_user_from_token called with device_id=%s", device_id)

    pattern = f"user:tokens:*:{device_id}"
    try:
        keys = [key async for key in keyvalue_adapter._client.scan_iter(match=pattern)]
        for key_bytes in keys:
            key = key_bytes
            token_json = await keyvalue_adapter.get_token(key)
            if not token_json:
                continue

            try:
                token_data = json.loads(token_json)
                if token_data.get("access_token") != access_token:
                    continue

                expires_at = token_data.get("expires_at")
                if expires_at and int(time.time()) > int(expires_at):
                    logger.warning("Access token expired for key: %s", key)
                    return AuthResponse(
                        user=None,
                        tokens=None,
                        error="Access token expired",
                        status_code=401
                    )

                # Extract user ID from Redis key
                user_id = key.split(":")[2]
                user = database_adapter.get_user_by_id(user_id)
                if not user:
                    logger.warning("User not found for ID: %s", user_id)
                    return AuthResponse(
                        user=None,
                        tokens=None,
                        error="User not found",
                        status_code=401
                    )

                logger.info("Token validated for user ID: %s", user_id)
                return AuthResponse(
                    user={
                        "id": user.id,
                        "email": user.email,
                        "name": getattr(user, "name", None)
                    },
                    tokens=None,
                    error=None,
                    status_code=200
                )
            except Exception as e:
                logger.warning("Failed to process token entry for key=%s: %s", key, str(e))
                continue

        logger.warning("No matching access token found")
        return AuthResponse(
            user=None,
            tokens=None,
            error="Invalid access token",
            status_code=401
        )
    except Exception as e:
        logger.exception("Unexpected error while verifying token: %s", str(e))
        return AuthResponse(
            user=None,
            tokens=None,
            error="Internal server error",
            status_code=500
        )
