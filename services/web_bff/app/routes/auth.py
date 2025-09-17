from fastapi import Request, Response, APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
import httpx, os, urllib.parse, logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
HUMAN_SERVICE_URL = os.getenv("HUMAN_SERVICE_URL", "http://human_service:8000")

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...)
):
    login_url = f"{AUTH_SERVICE_URL}/login"
    logger.debug("Proxying login request to %s", login_url)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            auth_response = await client.post(
                login_url,
                data={"email": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            logger.debug("Auth response: %d %s", auth_response.status_code, auth_response.text)
    except httpx.RequestError:
        logger.exception("Error contacting auth service for login")
        raise HTTPException(status_code=502, detail="Failed to contact auth service")

    if auth_response.status_code != 200:
        raise HTTPException(
            status_code=auth_response.status_code,
            detail=auth_response.json().get("detail", "Login failed"),
        )

    auth_json = auth_response.json()
    user = auth_json.get("user")
    if not user or "id" not in user:
        raise HTTPException(status_code=500, detail="Auth service did not return user id")

    user_id = user["id"]

    # Query human service for additional user info
    human_url = f"{HUMAN_SERVICE_URL}/{user_id}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            human_response = await client.get(human_url)
            logger.debug("Human service response: %d %s", human_response.status_code, human_response.text)
    except httpx.RequestError:
        logger.exception("Error contacting human service")
        raise HTTPException(status_code=502, detail="Failed to contact human service")

    if human_response.status_code != 200:
        raise HTTPException(
            status_code=human_response.status_code,
            detail="Failed to fetch user details from human service",
        )

    human_json = human_response.json()
    # Merge names and id into the user object
    user["first_name"] = human_json.get("first_name")
    user["middle_name"] = human_json.get("middle_name")
    user["last_name"] = human_json.get("last_name")
    user["id"] = human_json.get("id", user_id)  # prefer human id if present

    # Extract tokens from auth service response
    auth_cookies = auth_response.cookies
    tokens = auth_json.get("tokens", {})
    
    # CORRECT APPROACH: Refresh token in cookie, access token in response body
    response_data = {
        "user": user,
        "access_token": auth_cookies.get("access_token") or tokens.get("access_token"),
        "token_type": "bearer",
        "expires_in": 3600,
        "workspaces": [
            {
                "id": "workspace1",
                "name": "Workspace 1"
            }
        ],
        "last_accessed_workspace": {
            "id": "workspace1",
            "name": "Workspace 1"
        }
    }
    
    # Create JSONResponse
    json_response = JSONResponse(content=response_data)
    
    # Set ONLY the refresh token as a secure HttpOnly cookie
    refresh_token = auth_cookies.get("refresh_token") or tokens.get("refresh_token")
    if refresh_token:
        is_https = urllib.parse.urlparse(str(request.url)).scheme == "https"
        json_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_https,
            samesite="lax",
            path="/",
            max_age=7*24*3600  # 7 days for refresh token
        )
        logger.info("[AUTH] Set refresh_token as secure HttpOnly cookie")
    
    if response_data["access_token"]:
        logger.info("[AUTH] Returned access_token in response body for frontend")
    
    logger.info("[AUTH] Using CORRECT approach: refresh token in cookie, access token in response")
    
    return json_response

@router.get("/validate")
async def validate(request: Request):
    validate_url = f"{AUTH_SERVICE_URL}/validate"
    logger.debug("Proxying validate request to %s", validate_url)

    # Get cookies (for refresh token) and Authorization header (for access token)
    cookies = request.cookies
    headers = {}
    auth_header = request.headers.get("authorization")
    
    # If no Authorization header, check if we have a refresh token to get a new access token
    if not auth_header and "refresh_token" in cookies:
        logger.debug("No access token in Authorization header, but refresh token present in cookies")
        # For now, return a 401 to indicate frontend needs to use the access token
        # In a full implementation, you might want to automatically refresh the token here
        raise HTTPException(
            status_code=401,
            detail="Access token required in Authorization header. Use 'Bearer <access_token>' format."
        )
    
    if auth_header:
        headers["Authorization"] = auth_header
        logger.debug("Forwarding Authorization header to auth service")

    try:
        async with httpx.AsyncClient(timeout=10, cookies=cookies) as client:
            auth_response = await client.get(validate_url, headers=headers)
            logger.debug("Auth validate response: %d %s", auth_response.status_code, auth_response.text)
    except httpx.RequestError:
        logger.exception("Error contacting auth service for validate")
        raise HTTPException(status_code=502, detail="Failed to contact auth service")

    if auth_response.status_code != 200:
        raise HTTPException(
            status_code=auth_response.status_code,
            detail=auth_response.json().get("detail", "Validation failed"),
        )

    auth_json = auth_response.json()

    # Ensure output format is { "user": { ... } } even if backend returns user_id only
    if "user" in auth_json:
        return auth_json
    elif "user_id" in auth_json:
        return { "user": { "id": auth_json["user_id"] } }

    raise HTTPException(status_code=500, detail="Invalid validate response format")

@router.post("/logout")
async def logout(request: Request, response: Response):
    logout_url = f"{AUTH_SERVICE_URL}/logout"
    logger.debug("Proxying logout request to %s", logout_url)

    try:
        async with httpx.AsyncClient(timeout=10, cookies=request.cookies) as client:
            auth_response = await client.post(logout_url)
            logger.debug("Auth logout response: %d %s", auth_response.status_code, auth_response.text)
    except httpx.RequestError:
        logger.exception("Error contacting auth service for logout")
        raise HTTPException(status_code=502, detail="Failed to contact auth service")

    if auth_response.status_code != 200:
        raise HTTPException(
            status_code=auth_response.status_code,
            detail=auth_response.json().get("detail", "Logout failed"),
        )

    host_only = request.headers.get("host", "").split(":")[0]
    for name in request.cookies.keys():
        response.delete_cookie(name, domain=host_only, path="/")

    return auth_response.json()
