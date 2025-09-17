from uuid import UUID
from app.schemas.human import HumanResponse

class GetHuman:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> HumanResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return HumanResponse.from_orm(item)
