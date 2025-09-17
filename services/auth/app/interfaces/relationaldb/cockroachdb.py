from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.domain.user import User
from app.interfaces.relationaldb.relationaldb_repo import RelationalRepository
from app.infrastructure.db.schema.user_table import users
from app.common.utility import hash_password, verify_password

class CockroachUserRepository(RelationalRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(users).where(users.c.email == email).limit(1)
        result = self.session.execute(stmt).first()
        if result is None:
            return None
        return User.from_row(result)

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(users).where(users.c.id == user_id).limit(1)
        result = self.session.execute(stmt).first()
        if result is None:
            return None
        return User.from_row(result)

    def create_user(self, email: str, password: str) -> User:
        hashed_pw = hash_password(password)
        stmt = (
            insert(users)
            .values(
                email=email,
                password_hash=hashed_pw,
                email_verified=False,
                is_active=True
            )
            .returning(
                users.c.id,
                users.c.email,
                users.c.password_hash,
                users.c.email_verified,
                users.c.is_active
            )
        )
        result = self.session.execute(stmt).first()
        self.session.commit()
        return User.from_row(result)


    def verify_user_credentials(self, email: str, password: str) -> Optional[User]:
        stmt = select(users).where(users.c.email == email).limit(1)
        result = self.session.execute(stmt).first()
        if result is None:
            return None
        row = result._mapping
        if not verify_password(password, row["password_hash"]):
            return None
        return User.from_row(result)


    def update_user_password(self, user_id: UUID, new_password: str) -> None:
        hashed_pw = hash_password(new_password)
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(password_hash=hashed_pw)
        )
        self.session.execute(stmt)
        self.session.commit()

    def mark_email_verified(self, user_id: UUID) -> None:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(email_verified=True)
        )
        self.session.execute(stmt)
        self.session.commit()
