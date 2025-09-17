from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import datetime


from app.shared.enums import CommunicationEventType, CommunicationStatus



class Communication_eventBase(BaseModel):
    
    
    conversation_id: UUID
    
    workspace_id: str
    
    sender_id: Optional[UUID] = None
    
    recipient_id: Optional[UUID] = None
    
    external_contact: Optional[str] = None
    
    event_type: CommunicationEventType
    
    subject: Optional[str] = None
    
    body: Optional[str] = None
    
    status: CommunicationStatus
    
    summary: Optional[str] = None
    
    occurred_at: datetime
    
    created_at: Optional[datetime] = None
    
    created_by: UUID
    
    


class Communication_eventCreate(Communication_eventBase):
    pass


class Communication_eventUpdate(Communication_eventBase):
    pass


class Communication_eventResponse(Communication_eventBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
