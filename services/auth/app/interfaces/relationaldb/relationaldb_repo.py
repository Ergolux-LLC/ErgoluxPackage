from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.domain.user import User


class RelationalRepository(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Fetch a user by their unique identifier."""
        pass


    @abstractmethod
    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        user_id: Optional[UUID] = None
    ) -> User:
        """Create a new user. Password should already be hashed. Optionally accepts a user_id."""
        pass

    @abstractmethod
    def verify_user_credentials(self, email: str, password: str) -> Optional[User]:
        """Verify the user's password and return user if valid."""
        pass

    @abstractmethod
    def update_user_password(self, user_id: UUID, new_password: str) -> None:
        """Update the user’s password with a new hash."""
        pass

    @abstractmethod
    def mark_email_verified(self, user_id: UUID) -> None:
        """Mark the user as verified (after confirming token)."""
        pass
    
    @abstractmethod
    def reset_database(self) -> None:
        """Drop and recreate all tables."""
        pass