import logging
from fastapi import APIRouter, HTTPException, Request, Query
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.schemas.communication_event import (
    Communication_eventCreate,
    Communication_eventUpdate,
    Communication_eventResponse
)
from app.use_cases.create_communication_event import CreateCommunication_event
from app.use_cases.update_communication_event import UpdateCommunication_event
from app.use_cases.get_communication_event import GetCommunication_event
from app.use_cases.delete_communication_event import DeleteCommunication_event
from app.use_cases.search_communication_event import SearchCommunication_event

logger = logging.getLogger(__name__)

def get_communication_event_router(relational_db):
    router = APIRouter()

    @router.get("/", response_model=Dict[str, Any])
    def search_communication_events(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ):
        """
        Paginated search for communication_events.
        """
        filters = dict(request.query_params)
        filters.pop("limit", None)
        filters.pop("offset", None)
        logger.info(f"Searching communication_events with filters={filters}, limit={limit}, offset={offset}")
        try:
            results, total = SearchCommunication_event(relational_db).execute(limit=limit, offset=offset, **filters)
            results = [Communication_eventResponse.model_validate(obj) for obj in results]
            logger.info(f"Found {len(results)} communication_events (total={total})")
            return {
                "results": results,
                "limit": limit,
                "offset": offset,
                "total": total
            }
        except Exception as e:
            logger.exception(f"Exception during search for communication_events: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during search")

    @router.get("/{item_id}", response_model=Communication_eventResponse)
    def get_communication_event(item_id: UUID):
        logger.info(f"Fetching communication_event with id={item_id}")
        result = GetCommunication_event(relational_db).execute(item_id)
        if result is None:
            logger.warning(f"Communication_event with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Communication_event not found")
        return result

    @router.post("/", response_model=Communication_eventResponse)
    def create_communication_event(payload: Communication_eventCreate):
        logger.info(f"Creating new communication_event with payload={payload.dict()}")
        try:
            obj = CreateCommunication_event(relational_db).execute(payload)
            return obj
        except ValueError as e:
            logger.warning(f"HTTP error 400: {e} | Path: /")
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                # Extract column name from error message for better user feedback
                error_msg = str(e.orig)
                if "Key (" in error_msg and ")=" in error_msg:
                    # Extract field name from "Key (field_name)=(value) already exists"
                    field_name = error_msg.split("Key (")[1].split(")=")[0]
                    field_value = error_msg.split(")=(")[1].split(") already exists")[0]
                    detail = f"The {field_name} '{field_value}' is already in use. Please choose a different value."
                else:
                    detail = "A unique constraint was violated. Please check your input values."
                logger.warning(f"Unique constraint violation during create: {detail}")
                raise HTTPException(status_code=400, detail=detail)
            logger.error(f"Integrity error during create: {str(e.orig)}")
            raise HTTPException(status_code=400, detail=str(e.orig).split("\n")[0])
        except Exception as e:
            logger.exception(f"Exception during create for communication_event: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during create")

    @router.put("/{item_id}", response_model=Communication_eventResponse)
    def update_communication_event(item_id: UUID, payload: Communication_eventUpdate):
        logger.info(f"Updating communication_event with id={item_id}, payload={payload.dict(exclude_unset=True)}")
        try:
            updated = UpdateCommunication_event(relational_db).execute(item_id, payload)
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                # Extract column name from error message for better user feedback
                error_msg = str(e.orig)
                if "Key (" in error_msg and ")=" in error_msg:
                    # Extract field name from "Key (field_name)=(value) already exists"
                    field_name = error_msg.split("Key (")[1].split(")=")[0]
                    field_value = error_msg.split(")=(")[1].split(") already exists")[0]
                    detail = f"The {field_name} '{field_value}' is already in use. Please choose a different value."
                else:
                    detail = "A unique constraint was violated. Please check your input values."
                logger.warning(f"Unique constraint violation during update: {detail}")
                raise HTTPException(status_code=400, detail=detail)
            logger.error(f"Integrity error during update: {str(e.orig)}")
            raise HTTPException(status_code=400, detail=str(e.orig).split("\n")[0])
        except Exception as e:
            logger.exception(f"Exception during update for communication_event with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during update")
        if updated is None:
            logger.warning(f"Update failed: communication_event with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Communication_event not found")
        return updated

    @router.delete("/{item_id}")
    def delete_communication_event(item_id: UUID):
        logger.info(f"Deleting communication_event with id={item_id}")
        try:
            deleted = DeleteCommunication_event(relational_db).execute(item_id)
            if not deleted:
                logger.warning(f"Delete failed: communication_event with id={item_id} not found")
                raise HTTPException(status_code=404, detail="Communication_event not found")
            logger.info(f"Deleted communication_event with id={item_id}")
            return {"detail": "Communication_event deleted"}
        except Exception as e:
            logger.exception(f"Exception during delete for communication_event with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during delete")

    return router
