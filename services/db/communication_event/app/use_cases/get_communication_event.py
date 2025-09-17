from uuid import UUID
from app.schemas.communication_event import Communication_eventResponse

class GetCommunication_event:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> Communication_eventResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return Communication_eventResponse.from_orm(item)
