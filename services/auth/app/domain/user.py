from dataclasses import dataclass
from uuid import UUID
from typing import Any

@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    is_verified: bool
    is_active: bool
    first_name: str
    last_name: str

    @staticmethod
    def from_row(row: Any) -> "User":
        m = row._mapping
        return User(
            id=m["id"],
            email=m["email"],
            hashed_password=m["password_hash"],
            is_verified=m["email_verified"],
            is_active=m["is_active"],
            first_name=m["first_name"],
            last_name=m["last_name"]
        )
