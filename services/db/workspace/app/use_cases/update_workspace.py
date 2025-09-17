import logging
from uuid import UUID
from app.schemas.workspace import WorkspaceUpdate, WorkspaceResponse

logger = logging.getLogger(__name__)

class UpdateWorkspace:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: WorkspaceUpdate) -> WorkspaceResponse | None:
        try:
            logger.info(f"Updating workspace with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: workspace with id={item_id} not found")
                return None
            logger.info(f"Update successful for workspace with id={item_id}")
            return WorkspaceResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of workspace with id={item_id}: {e}")
            raise
