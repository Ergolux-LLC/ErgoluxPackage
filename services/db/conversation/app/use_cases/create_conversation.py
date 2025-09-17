import logging
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateConversation:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("conversation_type"):
            logger.warning("Missing required field: conversation_type")
            raise ValueError("Missing required field: conversation_type")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc)
        
        
        
        obj = self.db.create(data)
        return obj
