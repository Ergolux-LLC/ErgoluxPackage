import json
import time
import logging
from uuid import uuid4
from app.common.utility import generate_token
from app.common.config import Config
from app.interfaces.user_notification.reset_token_object import PasswordResetToken

logger = logging.getLogger(__name__)

async def forgot_password(
    config: Config,
    email: str,
    database_adapter,
    keyvalue_adapter,
    notifier
):
    user = database_adapter.get_user_by_email(email)
    if not user:
        logger.warning("Forgot password requested for unknown email: %s", email)
        return {
            "success": True,
            "message": "If this email is registered, a password reset link will be sent.",
            "status_code": 200
        }

    reset_token = generate_token()
    now = int(time.time())
    reset_token_ttl = int(config.get("PASSWORD_RESET_TOKEN_TTL"))
    reset_token_key = f"user:password_reset:{user.id}:{uuid4()}"

    token_data = PasswordResetToken(
        reset_token=reset_token,
        issued_at=now,
        expires_at=now + reset_token_ttl
    )

    redis_value = json.dumps(token_data.__dict__)
    await keyvalue_adapter.set_token(reset_token_key, redis_value, ex=reset_token_ttl)
    logger.info("Stored password reset token: key=%s, expires_in=%s", reset_token_key, reset_token_ttl)

    try:
        reset_link = f"{config.get('FRONTEND_RESET_URL')}?token={reset_token}"
        subject = "Password Reset Request"
        message = f"To reset your password, click the following link:\n\n{reset_link}\n\nIf you didn’t request this, ignore this message."

        notifier.connect()
        notifier.notify(recipient_id=user.email, subject=subject, message=message)
        notifier.disconnect()
    except Exception as e:
        logger.error("Failed to send password reset notification to %s: %s", user.email, e)
        return {
            "success": False,
            "message": "Failed to send password reset notification.",
            "status_code": 500
        }

    return {
        "success": True,
        "message": "If this email is registered, a password reset link will be sent.",
        "status_code": 200
    }
