from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import datetime




class Workspace_inviteBase(BaseModel):
    
    
    workspace_id: str
    
    email: str
    
    invited_by: UUID
    
    role: str
    
    invite_token: str
    
    created_at: Optional[datetime] = None
    
    expires_at: datetime
    
    accepted_at: Optional[datetime] = None
    
    created_by: UUID
    
    


class Workspace_inviteCreate(Workspace_inviteBase):
    pass


class Workspace_inviteUpdate(Workspace_inviteBase):
    pass


class Workspace_inviteResponse(Workspace_inviteBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
