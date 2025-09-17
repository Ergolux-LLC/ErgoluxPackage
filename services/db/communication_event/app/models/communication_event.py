from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Communication_event(Base):
    __tablename__ = "communication_event"
    
    
    id = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4 if True else None,
            nullable=False
        
    )
    
    conversation_id = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    workspace_id = Column(
        
            String,
            nullable=False
        
    )
    
    sender_id = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=True
        
    )
    
    recipient_id = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=True
        
    )
    
    external_contact = Column(
        
            String,
            nullable=True
        
    )
    
    event_type = Column(
        
            Enum,
            nullable=False
        
    )
    
    subject = Column(
        
            String,
            nullable=True
        
    )
    
    body = Column(
        
            String,
            nullable=True
        
    )
    
    status = Column(
        
            Enum,
            nullable=False
        
    )
    
    summary = Column(
        
            String,
            nullable=True
        
    )
    
    occurred_at = Column(
        
            DateTime,
            nullable=False
        
    )
    
    created_at = Column(
        
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    
