import logging
from app.models.communication_event import Communication_event
from app.schemas.communication_event import Communication_eventCreate, Communication_eventResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateCommunication_event:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("event_type"):
            logger.warning("Missing required field: event_type")
            raise ValueError("Missing required field: event_type")
        
        if not data.get("status"):
            logger.warning("Missing required field: status")
            raise ValueError("Missing required field: status")
        
        if not data.get("occurred_at"):
            logger.warning("Missing required field: occurred_at")
            raise ValueError("Missing required field: occurred_at")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("conversation_id"):
            data["conversation_id"] = uuid.uuid4()
        
        if not data.get("sender_id"):
            data["sender_id"] = uuid.uuid4()
        
        if not data.get("recipient_id"):
            data["recipient_id"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc)
        
        
        
        obj = self.db.create(data)
        return obj
