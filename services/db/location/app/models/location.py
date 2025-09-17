from .base import Base
from sqlalchemy import Column, DateTime, func, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Location(Base):
    __tablename__ = "location"
    
    
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
    
    name = Column(
        
            String,
            nullable=True
        
    )
    
    address_line1 = Column(
        
            String,
            nullable=False
        
    )
    
    address_line2 = Column(
        
            String,
            nullable=True
        
    )
    
    city = Column(
        
            String,
            nullable=False
        
    )
    
    state = Column(
        
            Enum,
            nullable=False
        
    )
    
    postal_code = Column(
        
            String,
            nullable=False
        
    )
    
    country = Column(
        
            String,
            nullable=False
        
    )
    
    latitude = Column(
        
            Float,
            nullable=True
        
    )
    
    longitude = Column(
        
            Float,
            nullable=True
        
    )
    
    location_type = Column(
        
            String,
            nullable=False
        
    )
    
    created_by = Column(
        
            PG_UUID(as_uuid=True),
            primary_key=False,
            default=uuid.uuid4 if False else None,
            nullable=False
        
    )
    
    
