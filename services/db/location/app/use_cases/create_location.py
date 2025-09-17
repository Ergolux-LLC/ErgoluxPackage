import logging
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateLocation:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("address_line1"):
            logger.warning("Missing required field: address_line1")
            raise ValueError("Missing required field: address_line1")
        
        if not data.get("city"):
            logger.warning("Missing required field: city")
            raise ValueError("Missing required field: city")
        
        if not data.get("state"):
            logger.warning("Missing required field: state")
            raise ValueError("Missing required field: state")
        
        if not data.get("postal_code"):
            logger.warning("Missing required field: postal_code")
            raise ValueError("Missing required field: postal_code")
        
        if not data.get("country"):
            logger.warning("Missing required field: country")
            raise ValueError("Missing required field: country")
        
        if not data.get("location_type"):
            logger.warning("Missing required field: location_type")
            raise ValueError("Missing required field: location_type")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        
        # Check for duplicate name (if applicable)
        existing = self.db.db.query(Location).filter_by(name=data["name"]).first()
        if existing:
            logger.warning("Location name must be unique: %s", data["name"])
            raise ValueError("Location name must be unique")
        
        
        obj = self.db.create(data)
        return obj
