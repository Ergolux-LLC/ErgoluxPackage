import logging
from app.models.human import Human
from app.schemas.human import HumanCreate, HumanResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateHuman:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        if "email" in data and data["email"] is not None:
            data["email"] = str(data["email"])
        
        if "linkedin_url" in data and data["linkedin_url"] is not None:
            data["linkedin_url"] = str(data["linkedin_url"])
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("first_name"):
            logger.warning("Missing required field: first_name")
            raise ValueError("Missing required field: first_name")
        
        if not data.get("last_name"):
            logger.warning("Missing required field: last_name")
            raise ValueError("Missing required field: last_name")
        
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
