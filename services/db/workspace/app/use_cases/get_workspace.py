from uuid import UUID
from app.schemas.workspace import WorkspaceResponse

class GetWorkspace:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> WorkspaceResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return WorkspaceResponse.from_orm(item)
