from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import datetime




class WorkspaceBase(BaseModel):
    
    name: str
    created_by: UUID
    owner_id: UUID
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(WorkspaceBase):
    pass


class WorkspaceResponse(WorkspaceBase):
    
    id: int
    obfuscated_id: str
    
    model_config = {
        "from_attributes": True
    }
