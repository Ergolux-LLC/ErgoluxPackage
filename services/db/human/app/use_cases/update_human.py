import logging
from uuid import UUID
from app.schemas.human import HumanUpdate, HumanResponse

logger = logging.getLogger(__name__)

class UpdateHuman:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: HumanUpdate) -> HumanResponse | None:
        try:
            logger.info(f"Updating human with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: human with id={item_id} not found")
                return None
            logger.info(f"Update successful for human with id={item_id}")
            return HumanResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of human with id={item_id}: {e}")
            raise
