from uuid import UUID
from app.schemas.location import LocationResponse

class GetLocation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> LocationResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return LocationResponse.from_orm(item)
