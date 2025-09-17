from pydantic import BaseModel

from typing import Optional
from uuid import UUID




from app.shared.enums import LocationType, USState



class LocationBase(BaseModel):
    
    
    workspace_id: str
    
    name: Optional[str] = None
    
    address_line1: str
    
    address_line2: Optional[str] = None
    
    city: str
    
    state: USState
    
    postal_code: str
    
    country: str
    
    latitude: Optional[float] = None
    
    longitude: Optional[float] = None
    
    location_type: LocationType
    
    created_by: UUID
    
    


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationResponse(LocationBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
