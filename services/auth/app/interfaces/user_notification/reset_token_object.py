from dataclasses import dataclass
import time

@dataclass
class PasswordResetToken:
    reset_token: str
    issued_at: int
    expires_at: int

    @staticmethod
    def create(reset_token: str, ip_address: str, user_agent: str,
               device_id: str, expires_in: int = 3600) -> 'PasswordResetToken':
        now = int(time.time())
        return PasswordResetToken(
            reset_token=reset_token,
            issued_at=now,
            expires_at=now + expires_in
        )
