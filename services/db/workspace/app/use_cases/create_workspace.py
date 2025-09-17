import logging
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateWorkspace:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Only keep allowed fields
        allowed = {"name", "created_by", "owner_id", "is_active", "created_at", "updated_at"}
        data = {k: v for k, v in data.items() if k in allowed}
        # Default is_active to True if not provided
        if "is_active" not in data or data["is_active"] is None:
            data["is_active"] = True
        # Set created_at if not provided
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc)
        
        obj = self.db.create(data)
        return obj
