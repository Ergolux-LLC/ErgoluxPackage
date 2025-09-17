from typing import Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import String
from uuid import UUID
import logging

from app.interfaces.relationaldb.relationaldb_repo import RelationalDBRepo
from app.models.workspace_member import Workspace_member
from app.infrastructure.database.postgres import SessionLocal

logger = logging.getLogger(__name__)


class PostGresAdapter(RelationalDBRepo):
    def __init__(self):
        logger.debug("Initializing PostGresAdapter for workspace_member")
        self.db: Session = SessionLocal()
        logger.info("SessionLocal created for PostGresAdapter")

    def get_all(self) -> List[Workspace_member]:
        logger.info("Fetching all workspace_member records")
        try:
            results = self.db.query(Workspace_member).all()
            logger.info("Fetched %d workspace_member records", len(results))
            return results
        except Exception as e:
            logger.error("Error fetching all workspace_member records: %s", e, exc_info=True)
            return []

    def get_by_id(self, item_id: UUID) -> Optional[Workspace_member]:
        logger.info("Fetching workspace_member by id: %s", item_id)
        try:
            result = self.db.query(Workspace_member).filter(Workspace_member.id == item_id).first()
            if result:
                logger.info("Found workspace_member with id: %s", item_id)
            else:
                logger.warning("No workspace_member found with id: %s", item_id)
            return result
        except Exception as e:
            logger.error("Error fetching workspace_member by id %s: %s", item_id, e, exc_info=True)
            return None

    def create(self, data: dict) -> Workspace_member:
        logger.info("Creating new workspace_member with data: %s", data)
        instance = Workspace_member(**data)
        self.db.add(instance)
        try:
            self.db.commit()
            self.db.refresh(instance)
            logger.info("Successfully created workspace_member: %s", instance)
            return instance
        except IntegrityError as e:
            self.db.rollback()
            logger.error("IntegrityError on create: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Unexpected error on create: %s", e, exc_info=True)
            raise

    def update(self, item_id: UUID, data: dict) -> Optional[Workspace_member]:
        logger.info("Updating workspace_member with id: %s and data: %s", item_id, data)
        instance = self.db.query(Workspace_member).filter(Workspace_member.id == item_id).first()
        if not instance:
            logger.warning("Update failed: Workspace_member with id %s not found", item_id)
            return None
        for key, value in data.items():
            logger.debug("Setting attribute %s to %s on workspace_member id %s", key, value, item_id)
            setattr(instance, key, value)
        try:
            self.db.commit()
            self.db.refresh(instance)
            logger.info("Successfully updated workspace_member: %s", instance)
            return instance
        except IntegrityError as e:
            self.db.rollback()
            logger.error("IntegrityError on update: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Unexpected error on update: %s", e, exc_info=True)
            raise

    def delete(self, item_id: UUID) -> bool:
        logger.info("Deleting workspace_member with id: %s", item_id)
        instance = self.db.query(Workspace_member).filter(Workspace_member.id == item_id).first()
        if not instance:
            logger.warning("Delete failed: Workspace_member with id %s not found", item_id)
            return False
        self.db.delete(instance)
        try:
            self.db.commit()
            logger.info("Successfully deleted workspace_member with id %s", item_id)
            return True
        except IntegrityError as e:
            self.db.rollback()
            logger.error("IntegrityError on delete: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Unexpected error on delete: %s", e, exc_info=True)
            raise

    def search(self, filters: dict) -> List[Workspace_member]:
        logger.info("Searching workspace_member with filters: %s", filters)
        query = self.db.query(Workspace_member)
        for field, value in filters.items():
            if hasattr(Workspace_member, field) and value is not None:
                column = getattr(Workspace_member, field)
                try:
                    if isinstance(value, str) and column.type.python_type == str:
                        logger.debug("Applying ilike filter on field '%s' with value '%s'", field, value)
                        query = query.filter(column.ilike(f"%{value}%"))
                    else:
                        logger.debug("Applying equality filter on field '%s' with value '%s'", field, value)
                        query = query.filter(column == value)
                except Exception as e:
                    logger.warning("Skipping filter for field '%s': %s", field, e)
        try:
            results = query.all()
            logger.info("Search returned %d result(s)", len(results))
            return results
        except Exception as e:
            logger.error("Error during search: %s", e, exc_info=True)
            return []
