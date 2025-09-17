import logging
from uuid import UUID
from app.schemas.conversation import ConversationUpdate, ConversationResponse

logger = logging.getLogger(__name__)

class UpdateConversation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: ConversationUpdate) -> ConversationResponse | None:
        try:
            logger.info(f"Updating conversation with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: conversation with id={item_id} not found")
                return None
            logger.info(f"Update successful for conversation with id={item_id}")
            return ConversationResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of conversation with id={item_id}: {e}")
            raise
