import logging
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class CreateTransaction:
    def __init__(self, db):
        self.db = db

    def execute(self, payload):
        data = payload.dict()
        
        # Convert Pydantic types to primitives (e.g., HttpUrl, EmailStr)
        
        # Explicitly check for required fields (defensive, in case validation is bypassed)
        
        if not data.get("workspace_id"):
            logger.warning("Missing required field: workspace_id")
            raise ValueError("Missing required field: workspace_id")
        
        if not data.get("transaction_date"):
            logger.warning("Missing required field: transaction_date")
            raise ValueError("Missing required field: transaction_date")
        
        if not data.get("sale_price"):
            logger.warning("Missing required field: sale_price")
            raise ValueError("Missing required field: sale_price")
        
        if not data.get("commission_rate"):
            logger.warning("Missing required field: commission_rate")
            raise ValueError("Missing required field: commission_rate")
        
        if not data.get("phase"):
            logger.warning("Missing required field: phase")
            raise ValueError("Missing required field: phase")
        
        if not data.get("status"):
            logger.warning("Missing required field: status")
            raise ValueError("Missing required field: status")
        
        # Auto-generate UUIDs for any UUID field if not provided
        
        if not data.get("id"):
            data["id"] = uuid.uuid4()
        
        if not data.get("agent_id"):
            data["agent_id"] = uuid.uuid4()
        
        if not data.get("location_id"):
            data["location_id"] = uuid.uuid4()
        
        if not data.get("buyer_id"):
            data["buyer_id"] = uuid.uuid4()
        
        if not data.get("seller_id"):
            data["seller_id"] = uuid.uuid4()
        
        if not data.get("created_by"):
            data["created_by"] = uuid.uuid4()
        
        # Set created_at if not provided
        
        
        
        obj = self.db.create(data)
        return obj
