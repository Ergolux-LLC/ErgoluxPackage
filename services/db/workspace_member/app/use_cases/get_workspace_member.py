from uuid import UUID
from app.schemas.workspace_member import Workspace_memberResponse

class GetWorkspace_member:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> Workspace_memberResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return Workspace_memberResponse.from_orm(item)
