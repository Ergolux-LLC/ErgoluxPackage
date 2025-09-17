import logging
from sqlalchemy import select, insert, update
from app.infrastructure.db.metadata import metadata
from typing import Optional
from uuid import UUID, uuid4

from app.domain.user import User
from app.interfaces.relationaldb.relationaldb_repo import RelationalRepository
from app.infrastructure.db.schema.user_table import users  
from app.common.utility import hash_password, verify_password
from app.infrastructure.db.postgres_driver import PostgresDriver
from app.common.config import Config

logger = logging.getLogger(__name__)

class PostgresUserAdapter(RelationalRepository):
    def __init__(self, config: Config):
        self._config = config
        driver = PostgresDriver(config)
        self.session = driver.get_session()
        logger.info("PostgresUserAdapter initialized with session %s", self.session)

    def get_user_by_email(self, email: str) -> Optional[User]:
        logger.debug("Fetching user by email: %s", email)
        stmt = select(users).where(users.c.email == email).limit(1)
        result = self.session.execute(stmt).first()
        logger.debug("Query result: %s", result)
        if result is None:
            return None
        return User.from_row(result)

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        logger.debug("Fetching user by ID: %s", user_id)
        stmt = select(users).where(users.c.id == user_id).limit(1)
        result = self.session.execute(stmt).first()
        logger.debug("Query result: %s", result)
        if result is None:
            return None
        return User.from_row(result)

    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        user_id: Optional[UUID] = None
    ) -> User:
        logger.info("Creating user with email: %s", email)

        if user_id is None:
            user_id = uuid4()
        elif not isinstance(user_id, UUID):
            raise TypeError("user_id must be a UUID")

        stmt = (
            insert(users)
            .values(
                id=user_id,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                email_verified=False,
                is_active=True
            )
            .returning(
                users.c.id,
                users.c.email,
                users.c.password_hash,
                users.c.first_name,
                users.c.last_name,
                users.c.email_verified,
                users.c.is_active
            )
        )
        result = self.session.execute(stmt).first()
        self.session.commit()
        logger.info("User created: %s", result)

        return User.from_row(result)


    def verify_user_credentials(self, email: str, password: str) -> Optional[User]:
        logger.info("Verifying credentials for: %s", email)
        stmt = select(users).where(users.c.email == email).limit(1)
        result = self.session.execute(stmt).first()
        logger.debug("User lookup result: %s", result)
        if result is None:
            return None
        row = result._mapping
        if not verify_password(password, row["password_hash"]):
            logger.warning("Password verification failed for user: %s", email)
            return None
        logger.info("Password verified for user: %s", email)
        return User.from_row(result)

    def update_user_password(self, user_id: UUID, new_password: str) -> None:
        logger.info("Updating password for user ID: %s", user_id)
        hashed_pw = hash_password(new_password)
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(password_hash=hashed_pw)
        )
        self.session.execute(stmt)
        self.session.commit()
        logger.info("Password updated for user ID: %s", user_id)

    def mark_email_verified(self, user_id: UUID) -> None:
        logger.info("Marking email verified for user ID: %s", user_id)
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(email_verified=True)
        )
        self.session.execute(stmt)
        self.session.commit()
        logger.info("Email marked as verified for user ID: %s", user_id)

    def reset_database(self) -> None:
        environment = self._config.get("ENVIRONMENT")
        logger.warning("Database reset requested. Current environment: %s", environment)
        if environment != "development":
            logger.warning("Skipping database reset in production environment")
            return
        logger.critical("Resetting database: dropping and recreating all tables")
        bind = self.session.get_bind()
        metadata.drop_all(bind=bind)
        logger.info("All tables dropped")
        metadata.create_all(bind=bind)
        logger.info("All tables recreated")