import logging
from uuid import UUID
from app.schemas.transaction import TransactionUpdate, TransactionResponse

logger = logging.getLogger(__name__)

class UpdateTransaction:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: TransactionUpdate) -> TransactionResponse | None:
        try:
            logger.info(f"Updating transaction with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: transaction with id={item_id} not found")
                return None
            logger.info(f"Update successful for transaction with id={item_id}")
            return TransactionResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of transaction with id={item_id}: {e}")
            raise
