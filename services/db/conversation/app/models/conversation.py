from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Conversation(Base):
    __tablename__ = "conversation"
    
    
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
    
    topic = Column(
        
            String,
            nullable=True
        
    )
    
    conversation_type = Column(
        
            Enum,
            nullable=False
        
    )
    
    summary = Column(
        
            String,
            nullable=True
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    created_at = Column(
        
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        
    )
    
    updated_at = Column(
        
            DateTime,
            nullable=True
        
    )
    
    
