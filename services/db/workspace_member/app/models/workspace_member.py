from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Workspace_member(Base):
    __tablename__ = "workspace_member"
    
    
    id = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4 if True else None,
            nullable=False
        
    )
    
    workspace_id = Column(
        
            String,
            nullable=False
        
    )
    
    role = Column(
        
            String,
            nullable=False
        
    )
    
    invited_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=True
        
    )
    
    joined_at = Column(
        
            DateTime,
            nullable=False
        
    )
    
    is_active = Column(
        
            Boolean,
            nullable=False
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    
