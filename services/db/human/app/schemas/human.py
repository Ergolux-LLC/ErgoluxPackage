from pydantic import BaseModel, EmailStr, HttpUrl

from typing import Optional
from uuid import UUID



from datetime import datetime




class HumanBase(BaseModel):
    
    
    workspace_id: str
    
    first_name: str
    
    last_name: str
    
    middle_name: Optional[str] = None
    
    email: Optional[EmailStr] = None
    
    phone_number: Optional[str] = None
    
    linkedin_url: Optional[HttpUrl] = None
    
    created_at: Optional[datetime] = None
    
    updated_at: Optional[datetime] = None
    
    created_by: UUID
    
    


class HumanCreate(HumanBase):
    pass


class HumanUpdate(HumanBase):
    pass


class HumanResponse(HumanBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
