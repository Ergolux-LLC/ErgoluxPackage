from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Workspace(Base):
    __tablename__ = "workspace"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    owner_id = Column(PG_UUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    @property
    def obfuscated_id(self):
        from app.utils.obfuscate import obfuscate_id
        return obfuscate_id(self.id)
    
