from uuid import UUID
from app.schemas.workspace_invite import Workspace_inviteResponse

class GetWorkspace_invite:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID) -> Workspace_inviteResponse | None:
        item = self.relational_db.get_by_id(item_id)
        if item is None:
            return None
        return Workspace_inviteResponse.from_orm(item)
