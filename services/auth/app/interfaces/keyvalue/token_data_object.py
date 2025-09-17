from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class UserToken:
    access_token: str
    refresh_token: str
    issued_at: int
    expires_at: int
    ip_address: str
    user_agent: str
    device_id: str
    session_id: str

    @staticmethod
    def create(access_token: str, refresh_token: str, ip_address: str, user_agent: str,
               device_id: str, session_id: str, expires_in: int = 3600) -> 'UserToken':
        now = int(time.time())
        return UserToken(
            access_token=access_token,
            refresh_token=refresh_token,
            issued_at=now,
            expires_at=now + expires_in,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            session_id=session_id
        )
