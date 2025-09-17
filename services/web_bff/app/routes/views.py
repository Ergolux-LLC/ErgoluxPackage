from fastapi import APIRouter, Query, Path, Body, Request, HTTPException, status
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import logging
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/views/directory", tags=["Human Directory"])

HUMAN_SERVICE_URL = "http://human_service:8000"

# --- Pydantic Models ---

class WorkspaceUserBase(BaseModel):
    workspace_id: str = Field(..., description="Workspace UUID")
    created_by: str = Field(..., description="User UUID (created by)")

class HumanCreate(BaseModel):
    workspace_id: str
    created_by: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None

class HumanBulkCreate(WorkspaceUserBase):
    humans: List[Dict[str, Any]]

class HumanBulkUpdate(WorkspaceUserBase):
    updates: List[Dict[str, Any]]

class HumanBulkDelete(WorkspaceUserBase):
    ids: List[str]

class HumanUpdate(WorkspaceUserBase):
    class Config:
        extra = "allow"

def log_httpx_error(e: httpx.HTTPStatusError, context: str = ""):
    request = e.request
    response = e.response
    logger.error(
        f"[{context}] Human service HTTP error:\n"
        f"  URL: {request.method} {request.url}\n"
        f"  Status: {response.status_code}\n"
        f"  Response: {response.text}\n"
        f"  Request headers: {dict(request.headers)}\n"
        f"  Request body: {request.content.decode() if request.content else None}"
    )

def log_unexpected_error(e: Exception, context: str = "", extra: dict = None):
    logger.exception(
        f"[{context}] Unexpected error calling human service"
        + (f" | Extra: {extra}" if extra else "")
    )

# --- Create ---

@router.post("", summary="Create a Single Human Record")
async def create_human(
    body: HumanCreate,
    request: Request,
):
    logger.info(f"Received create_human request: {body.json()}")
    logger.info(f"Workspace: {body.workspace_id}, Created By: {body.created_by}")
    # Log the raw request body for full visibility
    try:
        raw_body = await request.body()
        logger.info(f"RAW BODY SENT TO CREATE ENDPOINT: {raw_body!r}")
    except Exception as e:
        logger.warning(f"Could not log raw request body: {e}")

    try:
        # Log the exact payload being sent to the microservice
        payload = body.dict()
        logger.info(f"Payload sent to human microservice: {payload}")
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{HUMAN_SERVICE_URL}/", json=payload)
        resp.raise_for_status()
        logger.info(f"Human created successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "create_human")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "create_human", {"body": body.dict()})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

@router.post("/bulk", summary="Bulk Create Human Records")
async def bulk_create_humans(
    body: HumanBulkCreate,
    request: Request = None,
):
    logger.info(f"Received bulk_create_humans request: {body.json()}")
    logger.info(f"Workspace: {body.workspace_id}, Created By: {body.created_by}")
    try:
        payload = {"workspace_id": body.workspace_id, "user_id": body.created_by, "humans": body.humans}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{HUMAN_SERVICE_URL}/bulk", json=payload)
        resp.raise_for_status()
        logger.info(f"Bulk humans created successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "bulk_create_humans")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "bulk_create_humans", {"payload": payload})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

# --- Read ---

@router.get("", summary="Get Human Records")
async def get_humans(
    request: Request,
    workspace_id: str = Query(..., description="Workspace UUID"),
    created_by: Optional[str] = Query(None, description="User UUID (created by)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = None,
    sortBy: Optional[str] = None,
    sortDirection: Optional[str] = Query(None, regex="^(asc|desc)$"),
    fields: Optional[str] = None,
):
    logger.info(f"Received get_humans request: query_params={dict(request.query_params)}")
    logger.info(f"Workspace: {workspace_id}, Created By: {created_by}")
    params = dict(request.query_params)
    params.pop("workspace_id", None)
    params.pop("created_by", None)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{HUMAN_SERVICE_URL}/", params=params)
        resp.raise_for_status()
        logger.info(f"Humans fetched successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "get_humans")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "get_humans", {"params": params})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

@router.get("/{human_id}", summary="Get a Single Human Record")
async def get_human(
    human_id: str = Path(..., description="Human UUID"),
    request: Request = None,
):
    logger.info(f"Received get_human request for id={human_id}")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{HUMAN_SERVICE_URL}/{human_id}")
        resp.raise_for_status()
        logger.info(f"Human fetched successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "get_human")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "get_human", {"human_id": human_id})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

# --- Update ---

@router.patch("/bulk", summary="Bulk Update Human Records")
async def bulk_update_humans(
    body: HumanBulkUpdate,
    request: Request = None,
):
    logger.info(f"Received bulk_update_humans request: {body.json()}")
    logger.info(f"Workspace: {body.workspace_id}, Created By: {body.created_by}")
    try:
        payload = {"workspace_id": body.workspace_id, "user_id": body.created_by, "updates": body.updates}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{HUMAN_SERVICE_URL}/bulk", json=payload)
        resp.raise_for_status()
        logger.info(f"Bulk humans updated successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "bulk_update_humans")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "bulk_update_humans", {"payload": payload})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

@router.patch("/{id}", summary="Update a Single Human Record")
async def update_human(
    id: str = Path(...),
    body: Dict[str, Any] = Body(...),
    request: Request = None,
):
    workspace_id = body.get("workspace_id")
    user_id = body.get("user_id")
    if not workspace_id or not user_id:
        logger.warning(f"update_human: Missing workspace_id or user_id in body: {body}")
        raise HTTPException(status_code=422, detail="workspace_id and user_id are required in the body")
    updates = {k: v for k, v in body.items() if k not in ("workspace_id", "user_id")}
    logger.info(f"Received update_human request for id={id}: {body}")
    logger.info(f"Workspace: {workspace_id}, Created By: {user_id}")
    try:
        payload = {"workspace_id": workspace_id, "user_id": user_id, **updates}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{HUMAN_SERVICE_URL}/{id}", json=payload)
        resp.raise_for_status()
        logger.info(f"Human updated successfully for id={id}: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "update_human")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "update_human", {"id": id, "payload": payload})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

# --- Delete ---

@router.delete("/bulk", summary="Bulk Delete Human Records")
async def bulk_delete_humans(
    body: HumanBulkDelete,
    request: Request = None,
):
    logger.info(f"Received bulk_delete_humans request: {body.json()}")
    logger.info(f"Workspace: {body.workspace_id}, Created By: {body.created_by}")
    try:
        payload = {"workspace_id": body.workspace_id, "user_id": body.created_by, "ids": body.ids}
        async with httpx.AsyncClient() as client:
            resp = await client.request("DELETE", f"{HUMAN_SERVICE_URL}/bulk", json=payload)
        resp.raise_for_status()
        logger.info(f"Bulk humans deleted successfully: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "bulk_delete_humans")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "bulk_delete_humans", {"payload": payload})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")

@router.delete("/{id}", summary="Delete a Single Human Record")
async def delete_human(
    id: str = Path(...),
    body: WorkspaceUserBase = Body(...),
    request: Request = None,
):
    logger.info(f"Received delete_human request for id={id}: {body.json()}")
    logger.info(f"Workspace: {body.workspace_id}, Created By: {body.created_by}")
    try:
        payload = body.dict()
        async with httpx.AsyncClient() as client:
            resp = await client.request("DELETE", f"{HUMAN_SERVICE_URL}/{id}", json=payload)
        resp.raise_for_status()
        logger.info(f"Human deleted successfully for id={id}: {resp.json()}")
        return resp.json()
    except httpx.HTTPStatusError as e:
        log_httpx_error(e, "delete_human")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        log_unexpected_error(e, "delete_human", {"id": id, "payload": payload})
        raise HTTPException(status_code=500, detail="Internal error contacting human service")