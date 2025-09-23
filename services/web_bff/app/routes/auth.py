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

    # Query human service for additional user info by created_by field
    human_url = f"{HUMAN_SERVICE_URL}/?created_by={user_id}&limit=1"
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

    # Human service returns paginated results, get first result
    human_data = human_response.json()
    if not human_data.get("results") or len(human_data["results"]) == 0:
        raise HTTPException(
            status_code=404,
            detail="No human profile found for this user",
        )

    # Human service returns paginated results, get first result
    human_data = human_response.json()
    if not human_data.get("results") or len(human_data["results"]) == 0:
        raise HTTPException(
            status_code=404,
            detail="No human profile found for this user",
        )

    human_json = human_data["results"][0]  # Get first human record
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
        # For cross-site cookies (custom dev domains), must use SameSite=None and Secure=True
        import os
        env = os.getenv("ENV", "dev").lower()
        if env == "prod":
            json_response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="none",
                path="/",
                domain=".app.ergolux.io",
                max_age=7*24*3600
            )
            logger.info("[AUTH] Set refresh_token as Secure, SameSite=None cookie for cross-site context, domain=.app.ergolux.io")
        else:
            json_response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="none",
                path="/",
                max_age=7*24*3600
            )
            logger.info("[AUTH] Set refresh_token as Secure, SameSite=None cookie for cross-site context, no domain (dev)")
    
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

@router.post("/refresh")
async def refresh(request: Request, response: Response):
    """
    Proxy refresh token request to auth service
    """
    refresh_url = f"{AUTH_SERVICE_URL}/refresh"
    logger.info("Proxying refresh request to %s", refresh_url)
    
    # Debug: Log incoming cookies
    cookies = request.cookies
    logger.info("Incoming cookies: %s", dict(cookies))
    
    # Check if refresh token is present
    refresh_token = cookies.get("refresh_token")
    if not refresh_token:
        logger.error("No refresh_token found in cookies: %s", dict(cookies))
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    logger.info("Found refresh_token: %s...", refresh_token[:20] if refresh_token else "None")
    
    try:
        # Forward request with proper cookie handling
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": request.headers.get("user-agent", "web-bff")
        }
        
        # FIXED: Use cookies parameter instead of headers for httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            auth_response = await client.post(
                refresh_url,
                headers=headers,
                cookies=cookies  # This properly forwards cookies to auth service
            )
        
        logger.info("Auth service response status: %s", auth_response.status_code)
        
    except httpx.RequestError as e:
        logger.error("Network error when calling auth service: %s", str(e))
        raise HTTPException(status_code=502, detail="Authentication service unavailable")
    
    if auth_response.status_code != 200:
        logger.warning("Auth service refresh failed with status %s", auth_response.status_code)
        try:
            error_detail = auth_response.json()
            logger.error("Auth service error details: %s", error_detail)
        except:
            error_detail = {"detail": "Token refresh failed"}
        
        raise HTTPException(
            status_code=auth_response.status_code,
            detail=error_detail.get("detail", "Token refresh failed")
        )
    
    auth_json = auth_response.json()
    logger.info("Token refresh successful")
    
    # Extract token data from auth service response
    tokens = auth_json.get("tokens", {})
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    
    if not access_token or not refresh_token:
        logger.error("Missing tokens in auth service response: %s", auth_json)
        raise HTTPException(status_code=500, detail="Auth service did not return complete tokens")
    
    # Create response with access token in body (same pattern as login)
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour default
            "user": auth_json.get("user")
        }
    )
    
    # Set NEW refresh token as HttpOnly cookie (same pattern as login)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
        samesite="none",
        secure=True
    )
    
    logger.info("Set new refresh token cookie and returned access token in response body")
    return response

@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Proxy logout request to auth service
    """
    logout_url = f"{AUTH_SERVICE_URL}/logout"
    logger.info("Proxying logout request to %s", logout_url)
    
    try:
        # Forward cookies and headers
        cookies = request.cookies
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": request.headers.get("user-agent", "web-bff")
        }
        
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                logout_url,
                headers=headers,
                cookies=cookies,
                timeout=30.0
            )
        
    except httpx.RequestError as e:
        logger.error("Network error during logout: %s", str(e))
        # Even if auth service is down, clear cookies locally
        pass
    
    # Clear cookies regardless of auth service response
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/", httponly=True)
    
    logger.info("Logout completed, cookies cleared")
    return {"detail": "Logged out successfully"}
