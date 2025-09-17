from uuid import UUID
from app.schemas.transaction import TransactionResponse

class GetTransaction:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> TransactionResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return TransactionResponse.from_orm(item)
