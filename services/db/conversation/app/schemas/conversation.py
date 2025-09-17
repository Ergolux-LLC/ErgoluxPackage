from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import datetime


from app.shared.enums import ConversationType



class ConversationBase(BaseModel):
    
    
    workspace_id: str
    
    topic: Optional[str] = None
    
    conversation_type: ConversationType
    
    summary: Optional[str] = None
    
    created_by: UUID
    
    created_at: Optional[datetime] = None
    
    updated_at: Optional[datetime] = None
    
    


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
