from pydantic import BaseModel

from typing import Optional
from uuid import UUID



from datetime import date


from app.shared.enums import TransactionPhase, TransactionStatus



class TransactionBase(BaseModel):
    
    
    workspace_id: str
    
    agent_id: UUID
    
    location_id: UUID
    
    buyer_id: Optional[UUID] = None
    
    seller_id: Optional[UUID] = None
    
    transaction_date: date
    
    sale_price: float
    
    commission_rate: float
    
    phase: TransactionPhase
    
    status: TransactionStatus
    
    created_by: UUID
    
    


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    
    id: UUID
    
    model_config = {
        "from_attributes": True
    }
