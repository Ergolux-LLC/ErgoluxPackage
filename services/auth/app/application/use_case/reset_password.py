import logging
import json
import time
import re

from app.common.utility import hash_password
from app.common.config import Config

logger = logging.getLogger(__name__)

async def reset_password(
    token: str,
    new_password: str,
    config: Config,
    database_adapter,
    keyvalue_adapter
):
    logger.info("Reset password requested")

    # Search Redis for matching reset token
    pattern = "user:password_reset:*"
    matching_key = None
    token_data = None
    keys = await keyvalue_adapter.get_keys(pattern)

    for key in keys:
        raw = await keyvalue_adapter.get_token(key)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
            if parsed.get("reset_token") == token:
                matching_key = key
                token_data = parsed
                break
        except Exception as e:
            logger.warning("Failed to parse token JSON from key %s: %s", key, e)

    if not matching_key or not token_data:
        logger.warning("Reset token not found or invalid")
        return {
            "success": False,
            "message": "Invalid or expired reset token.",
            "status_code": 400
        }

    # Validate token expiration
    now = int(time.time())
    if now > token_data.get("expires_at", 0):
        logger.warning("Reset token expired: %s", token)
        await keyvalue_adapter.delete_token(matching_key)
        return {
            "success": False,
            "message": "Reset token has expired.",
            "status_code": 400
        }

    # Extract user_id from key format
    match = re.match(r"user:password_reset:(.+?):", matching_key)
    if not match:
        logger.error("Failed to extract user ID from key: %s", matching_key)
        return {
            "success": False,
            "message": "Malformed reset token.",
            "status_code": 400
        }

    user_id = match.group(1)

    try:
        database_adapter.update_user_password(user_id, new_password)
        await keyvalue_adapter.delete_token(matching_key)
        logger.info("Password successfully reset for user_id: %s", user_id)
    except Exception as e:
        logger.error("Failed to update password for user_id %s: %s", user_id, e)
        return {
            "success": False,
            "message": "Unable to reset password.",
            "status_code": 500
        }

    return {
        "success": True,
        "message": "Password has been reset.",
        "status_code": 200
    }
