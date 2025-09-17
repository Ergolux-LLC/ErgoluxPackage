from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Workspace_invite(Base):
    __tablename__ = "workspace_invite"
    
    
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
    
    email = Column(
        
            String,
            nullable=False
        
    )
    
    invited_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    role = Column(
        
            String,
            nullable=False
        
    )
    
    invite_token = Column(
        
            String,
            nullable=False
        
    )
    
    created_at = Column(
        
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        
    )
    
    expires_at = Column(
        
            DateTime,
            nullable=False
        
    )
    
    accepted_at = Column(
        
            DateTime,
            nullable=True
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    
