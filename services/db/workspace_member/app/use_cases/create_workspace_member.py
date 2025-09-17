import logging
from app.models.workspace_member import Workspace_member
from app.schemas.workspace_member import Workspace_memberCreate, Workspace_memberResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateWorkspace_member:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("role"):
            logger.warning("Missing required field: role")
            raise ValueError("Missing required field: role")
        
        if not data.get("joined_at"):
            logger.warning("Missing required field: joined_at")
            raise ValueError("Missing required field: joined_at")
        
        if not data.get("is_active"):
            logger.warning("Missing required field: is_active")
            raise ValueError("Missing required field: is_active")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("invited_by"):
            data["invited_by"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        
        
        obj = self.db.create(data)
        return obj
