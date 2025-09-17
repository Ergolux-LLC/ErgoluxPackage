from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import datetime




class Workspace_memberBase(BaseModel):
    
    
    workspace_id: str
    
    role: str
    
    invited_by: Optional[UUID] = None
    
    joined_at: datetime
    
    is_active: bool
    
    created_by: UUID
    
    


class Workspace_memberCreate(Workspace_memberBase):
    pass


class Workspace_memberUpdate(Workspace_memberBase):
    pass


class Workspace_memberResponse(Workspace_memberBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
