import logging
from app.models.workspace_invite import Workspace_invite
from app.schemas.workspace_invite import Workspace_inviteCreate, Workspace_inviteResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateWorkspace_invite:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("email"):
            logger.warning("Missing required field: email")
            raise ValueError("Missing required field: email")
        
        if not data.get("role"):
            logger.warning("Missing required field: role")
            raise ValueError("Missing required field: role")
        
        if not data.get("invite_token"):
            logger.warning("Missing required field: invite_token")
            raise ValueError("Missing required field: invite_token")
        
        if not data.get("expires_at"):
            logger.warning("Missing required field: expires_at")
            raise ValueError("Missing required field: expires_at")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("invited_by"):
            data["invited_by"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc)
        
        
        
        obj = self.db.create(data)
        return obj
