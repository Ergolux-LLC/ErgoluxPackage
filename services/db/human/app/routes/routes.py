import logging
from fastapi import APIRouter, HTTPException, Request, Query
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.schemas.human import (
    HumanCreate,
    HumanUpdate,
    HumanResponse
)
from app.use_cases.create_human import CreateHuman
from app.use_cases.update_human import UpdateHuman
from app.use_cases.get_human import GetHuman
from app.use_cases.delete_human import DeleteHuman
from app.use_cases.search_human import SearchHuman

logger = logging.getLogger(__name__)

def get_human_router(relational_db):
    router = APIRouter()

    @router.get("/", response_model=Dict[str, Any])
    def search_humans(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ):
        """
        Paginated search for humans.
        """
        filters = dict(request.query_params)
        filters.pop("limit", None)
        filters.pop("offset", None)
        logger.info(f"Searching humans with filters={filters}, limit={limit}, offset={offset}")
        try:
            results, total = SearchHuman(relational_db).execute(limit=limit, offset=offset, **filters)
            results = [HumanResponse.model_validate(obj) for obj in results]
            logger.info(f"Found {len(results)} humans (total={total})")
            return {
                "results": results,
                "limit": limit,
                "offset": offset,
                "total": total
            }
        except Exception as e:
            logger.exception(f"Exception during search for humans: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during search")

    @router.get("/{item_id}", response_model=HumanResponse)
    def get_human(item_id: UUID):
        logger.info(f"Fetching human with id={item_id}")
        result = GetHuman(relational_db).execute(item_id)
        if result is None:
            logger.warning(f"Human with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Human not found")
        return result

    @router.post("/", response_model=HumanResponse)
    def create_human(payload: HumanCreate):
        logger.info(f"Creating new human with payload={payload.dict()}")
        try:
            obj = CreateHuman(relational_db).execute(payload)
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
            logger.exception(f"Exception during create for human: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during create")

    @router.put("/{item_id}", response_model=HumanResponse)
    def update_human(item_id: UUID, payload: HumanUpdate):
        logger.info(f"Updating human with id={item_id}, payload={payload.dict(exclude_unset=True)}")
        try:
            updated = UpdateHuman(relational_db).execute(item_id, payload)
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
            logger.exception(f"Exception during update for human with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during update")
        if updated is None:
            logger.warning(f"Update failed: human with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Human not found")
        return updated

    @router.delete("/{item_id}")
    def delete_human(item_id: UUID):
        logger.info(f"Deleting human with id={item_id}")
        try:
            deleted = DeleteHuman(relational_db).execute(item_id)
            if not deleted:
                logger.warning(f"Delete failed: human with id={item_id} not found")
                raise HTTPException(status_code=404, detail="Human not found")
            logger.info(f"Deleted human with id={item_id}")
            return {"detail": "Human deleted"}
        except Exception as e:
            logger.exception(f"Exception during delete for human with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during delete")

    return router
