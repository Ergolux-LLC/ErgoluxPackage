import logging
from uuid import UUID
from app.schemas.communication_event import Communication_eventUpdate, Communication_eventResponse

logger = logging.getLogger(__name__)

class UpdateCommunication_event:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: Communication_eventUpdate) -> Communication_eventResponse | None:
        try:
            logger.info(f"Updating communication_event with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: communication_event with id={item_id} not found")
                return None
            logger.info(f"Update successful for communication_event with id={item_id}")
            return Communication_eventResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of communication_event with id={item_id}: {e}")
            raise
