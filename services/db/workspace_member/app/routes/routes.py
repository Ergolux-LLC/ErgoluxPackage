import logging
from fastapi import APIRouter, HTTPException, Request, Query
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.schemas.workspace_member import (
    Workspace_memberCreate,
    Workspace_memberUpdate,
    Workspace_memberResponse
)
from app.use_cases.create_workspace_member import CreateWorkspace_member
from app.use_cases.update_workspace_member import UpdateWorkspace_member
from app.use_cases.get_workspace_member import GetWorkspace_member
from app.use_cases.delete_workspace_member import DeleteWorkspace_member
from app.use_cases.search_workspace_member import SearchWorkspace_member

logger = logging.getLogger(__name__)

def get_workspace_member_router(relational_db):
    router = APIRouter()

    @router.get("/", response_model=Dict[str, Any])
    def search_workspace_members(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ):
        """
        Paginated search for workspace_members.
        """
        filters = dict(request.query_params)
        filters.pop("limit", None)
        filters.pop("offset", None)
        logger.info(f"Searching workspace_members with filters={filters}, limit={limit}, offset={offset}")
        try:
            results, total = SearchWorkspace_member(relational_db).execute(limit=limit, offset=offset, **filters)
            results = [Workspace_memberResponse.model_validate(obj) for obj in results]
            logger.info(f"Found {len(results)} workspace_members (total={total})")
            return {
                "results": results,
                "limit": limit,
                "offset": offset,
                "total": total
            }
        except Exception as e:
            logger.exception(f"Exception during search for workspace_members: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during search")

    @router.get("/{item_id}", response_model=Workspace_memberResponse)
    def get_workspace_member(item_id: UUID):
        logger.info(f"Fetching workspace_member with id={item_id}")
        result = GetWorkspace_member(relational_db).execute(item_id)
        if result is None:
            logger.warning(f"Workspace_member with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Workspace_member not found")
        return result

    @router.post("/", response_model=Workspace_memberResponse)
    def create_workspace_member(payload: Workspace_memberCreate):
        logger.info(f"Creating new workspace_member with payload={payload.dict()}")
        try:
            obj = CreateWorkspace_member(relational_db).execute(payload)
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
            logger.exception(f"Exception during create for workspace_member: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during create")

    @router.put("/{item_id}", response_model=Workspace_memberResponse)
    def update_workspace_member(item_id: UUID, payload: Workspace_memberUpdate):
        logger.info(f"Updating workspace_member with id={item_id}, payload={payload.dict(exclude_unset=True)}")
        try:
            updated = UpdateWorkspace_member(relational_db).execute(item_id, payload)
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
            logger.exception(f"Exception during update for workspace_member with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during update")
        if updated is None:
            logger.warning(f"Update failed: workspace_member with id={item_id} not found")
            raise HTTPException(status_code=404, detail="Workspace_member not found")
        return updated

    @router.delete("/{item_id}")
    def delete_workspace_member(item_id: UUID):
        logger.info(f"Deleting workspace_member with id={item_id}")
        try:
            deleted = DeleteWorkspace_member(relational_db).execute(item_id)
            if not deleted:
                logger.warning(f"Delete failed: workspace_member with id={item_id} not found")
                raise HTTPException(status_code=404, detail="Workspace_member not found")
            logger.info(f"Deleted workspace_member with id={item_id}")
            return {"detail": "Workspace_member deleted"}
        except Exception as e:
            logger.exception(f"Exception during delete for workspace_member with id={item_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during delete")

    return router
