from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Human(Base):
    __tablename__ = "human"
    
    
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
    
    first_name = Column(
        
            String,
            nullable=False
        
    )
    
    last_name = Column(
        
            String,
            nullable=False
        
    )
    
    middle_name = Column(
        
            String,
            nullable=True
        
    )
    
    email = Column(
        
            String,
            nullable=True
        
    )
    
    phone_number = Column(
        
            String,
            nullable=True
        
    )
    
    linkedin_url = Column(
        
            String,
            nullable=True
        
    )
    
    created_at = Column(
        
            DateTime(timezone=True),
            nullable=True,
            server_default=func.now()
        
    )
    
    updated_at = Column(
        
            DateTime,
            nullable=True
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    
