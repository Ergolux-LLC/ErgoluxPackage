from uuid import UUID
from app.schemas.conversation import ConversationResponse

class GetConversation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> ConversationResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return ConversationResponse.from_orm(item)
