import logging
from uuid import UUID
from app.schemas.location import LocationUpdate, LocationResponse

logger = logging.getLogger(__name__)

class UpdateLocation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, item_id: UUID, payload: LocationUpdate) -> LocationResponse | None:
        try:
            logger.info(f"Updating location with id={item_id} and payload={payload.dict(exclude_unset=True)}")
            data = payload.dict(exclude_unset=True)
            updated = self.relational_db.update(item_id, data)
            if updated is None:
                logger.warning(f"Update failed: location with id={item_id} not found")
                return None
            logger.info(f"Update successful for location with id={item_id}")
            return LocationResponse.from_orm(updated)
        except Exception as e:
            logger.exception(f"Exception during update of location with id={item_id}: {e}")
            raise
