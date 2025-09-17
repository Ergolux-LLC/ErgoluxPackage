from sqlalchemy import Table, Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.infrastructure.db.metadata import metadata

users = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("email_verified", Boolean, nullable=False),
    Column("is_active", Boolean, nullable=False),
)
