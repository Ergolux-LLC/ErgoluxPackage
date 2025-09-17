from fastapi import APIRouter, Depends, Request, HTTPException, Cookie
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.common.config import Config
from app.application.use_case.get_user_from_token import get_user_from_token
from app.interfaces.relationaldb.relationaldb_repo import RelationalRepository
from app.interfaces.keyvalue.keyvalue_repo import KeyValueRepository

logger = logging.getLogger(__name__)

def get_relational_adapter() -> RelationalRepository:
    from app.main import relational_db_adapter
    return relational_db_adapter

def get_keyvalue_adapter() -> KeyValueRepository:
    from app.main import keyvalue_adapter
    return keyvalue_adapter

def get_config() -> Config:
    from app.main import config
    return config

internal_router = APIRouter(prefix="/api/internal", tags=["internal"])

@internal_router.get("/validate")
async def validate(
    request: Request,
    access_token: Optional[str] = Cookie(default=None),
    repo: RelationalRepository = Depends(get_relational_adapter),
    kv: KeyValueRepository = Depends(get_keyvalue_adapter),
    config: Config = Depends(get_config),
):
    logger.info(f"[internal.validate] method={request.method} url={request.url}")

    logger.info("[internal.validate] headers:")
    for k, v in request.headers.items():
        logger.info(f"  {k}: {v}")

    logger.info("[internal.validate] cookies:")
    for k, v in request.cookies.items():
        logger.info(f"  {k}: {v}")

    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
            logger.info(f"[internal.validate] access_token from Authorization header: {access_token}")
        else:
            logger.warning("[internal.validate] Missing access token in cookie or Authorization header")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing access token. Check 'access_token' cookie or 'Authorization' header."}
            )

    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "unknown")
    device_id = request.headers.get("X-Device-ID", "web_browser")

    logger.info(f"[internal.validate] ip={ip_address}, user_agent={user_agent}, device_id={device_id}")

    auth_response = await get_user_from_token(
        access_token=access_token,
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        database_adapter=repo,
        keyvalue_adapter=kv,
        config=config
    )

    if auth_response.error or not auth_response.user:
        logger.warning(f"[internal.validate] auth failed: {auth_response.error}")
        return JSONResponse(
            status_code=auth_response.status_code,
            content={"error": auth_response.error or "User not found"}
        )

    logger.info(f"[internal.validate] validated user_id={auth_response.user['id']}")
    return {"user_id": auth_response.user["id"]}
