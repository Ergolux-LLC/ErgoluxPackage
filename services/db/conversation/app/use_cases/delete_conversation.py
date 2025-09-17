from uuid import UUID

class DeleteConversation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> bool:
        return self.relational_db.delete(item_id)
