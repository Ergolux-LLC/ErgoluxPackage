from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.responses import Response as StarletteResponse
from starlette.datastructures import MutableHeaders
from pydantic import BaseModel
from typing import Optional
import os
import logging
import json

router = APIRouter(tags=["Development"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dev")

def is_dev_mode():
    """Check if the application is running in development mode"""
    env_var = os.getenv("ENV", "dev").lower()
    return env_var in ["development", "dev"]

class CookieTestResponse(BaseModel):
    """Response model for cookie test"""
    success: bool
    message: str
    cookies_set: list[str]
    set_cookie_headers: list[str]
    
class CookieCheckResponse(BaseModel):
    """Response model for cookie verification"""
    authenticated: bool
    access_token_present: bool
    refresh_token_present: bool
    test_cookie_present: bool
    access_token_preview: Optional[str] = None
    refresh_token_preview: Optional[str] = None
    test_cookie_value: Optional[str] = None
    all_cookies: dict[str, str]
    request_cookie_header: Optional[str] = None

class CookieHeaderCheckResponse(BaseModel):
    """Response model for header verification"""
    response_headers: dict[str, str]
    set_cookie_headers: list[str]
    message: str

@router.get("/dev/cookie-headers", 
           response_model=CookieHeaderCheckResponse,
           summary="Check response headers (Dev Mode Only)",
           description="""
Development-only endpoint that shows what Set-Cookie headers are actually being sent.
""")
async def dev_cookie_headers(response: Response):
    """
    Development-only endpoint to inspect response headers.
    
    Sets test cookies and returns what headers are actually being sent.
    
    Raises:
        HTTPException: If not in development mode
    """
    if not is_dev_mode():
        raise HTTPException(
            status_code=404,
            detail="This endpoint is only available in development mode"
        )
    
    logger.info("[DEV] === COOKIE HEADERS CHECK ===")
    
    # Set test cookies
    response.set_cookie("test1", "value1", httponly=True, path="/")
    response.set_cookie("test2", "value2", httponly=True, path="/")
    
    # Also try manual headers
    response.headers.append("Set-Cookie", "manual1=manualvalue1; HttpOnly; Path=/")
    response.headers.append("Set-Cookie", "manual2=manualvalue2; HttpOnly; Path=/")
    
    # Get all headers
    all_headers = dict(response.headers)
    set_cookie_headers = response.headers.getlist("Set-Cookie") if hasattr(response.headers, 'getlist') else []
    
    logger.info(f"[DEV] Response headers: {all_headers}")
    logger.info(f"[DEV] Set-Cookie headers: {set_cookie_headers}")
    
    return CookieHeaderCheckResponse(
        response_headers=all_headers,
        set_cookie_headers=set_cookie_headers,
        message=f"Headers check complete. Found {len(set_cookie_headers)} Set-Cookie headers."
    )

@router.post("/dev/cookie-test", 
           summary="Test cookie setting (Dev Mode Only)",
           description="""
Development-only endpoint that sets test auth cookies to verify cookie functionality.
Sets both access_token and refresh_token cookies like the real auth flow.
""")
async def dev_cookie_test():
    """
    Development-only endpoint to test cookie setting.
    
    Sets test access_token and refresh_token cookies plus a test cookie.
    Uses JSONResponse to manually control Set-Cookie headers.
    
    Raises:
        HTTPException: If not in development mode
    """
    if not is_dev_mode():
        raise HTTPException(
            status_code=404,
            detail="This endpoint is only available in development mode"
        )
    
    logger.info("[DEV] === COOKIE TEST START (FIXED VERSION) ===")
    
    # Test values that mimic real auth tokens
    test_access_token = "TEST_ACCESS_TOKEN_1234567890abcdef"
    test_refresh_token = "TEST_REFRESH_TOKEN_abcdef1234567890"
    test_cookie_value = "test_value_12345"
    
    cookies_set = ["access_token", "refresh_token", "test_cookie"]
    
    # Create all Set-Cookie headers manually
    set_cookie_headers = [
        f"access_token={test_access_token}; HttpOnly; Path=/; SameSite=lax; Max-Age=3600",
        f"refresh_token={test_refresh_token}; HttpOnly; Path=/; SameSite=lax; Max-Age=3600", 
        f"test_cookie={test_cookie_value}; Path=/; SameSite=lax; Max-Age=3600"
    ]
    
    # CORRECT APPROACH: Refresh token in cookie, access token in response body
    response_data = {
        "success": True,
        "message": "CORRECT: Refresh token in cookie, access token in response body",
        "access_token": test_access_token,  # Frontend gets this
        "token_type": "bearer",
        "expires_in": 3600,
        "cookies_set": ["refresh_token"],  # Only refresh token in cookie
    }
    
    # Create JSONResponse
    response = JSONResponse(content=response_data)
    
    # Set ONLY the refresh token as a secure cookie
    response.set_cookie(
        key="refresh_token",
        value=test_refresh_token,
        httponly=True,
        secure=False,  # False for localhost development
        path="/",
        samesite="lax",
        max_age=7*24*3600  # 7 days for refresh token
    )
    
    logger.info("[DEV] Set refresh_token as secure HttpOnly cookie")
    logger.info("[DEV] Returned access_token in response body for frontend")
    logger.info("[DEV] === COOKIE TEST COMPLETE (CORRECT APPROACH) ===")
    
    return response

@router.get("/dev/cookie-check", 
           response_model=CookieCheckResponse,
           summary="Cookie verification API (Dev Mode Only)",
           description="""
Development-only endpoint that checks if server-side authentication cookies are properly set.
Returns JSON with cookie status information.
""")
async def dev_cookie_check(request: Request):
    """
    Development-only endpoint to verify authentication cookies.
    
    Returns JSON with:
    - Overall authentication status
    - Individual cookie presence status
    - Masked token previews for verification
    - Complete cookie analysis
    
    Raises:
        HTTPException: If not in development mode
    """
    if not is_dev_mode():
        raise HTTPException(
            status_code=404,
            detail="This endpoint is only available in development mode"
        )
    
    logger.info("[DEV] === COOKIE CHECK START ===")
    
    # Log raw cookie header from request
    cookie_header = request.headers.get("cookie", "")
    logger.info(f"[DEV] Raw cookie header: '{cookie_header}'")
    
    # Extract all cookies from request
    all_cookies = dict(request.cookies)
    logger.info(f"[DEV] All cookies parsed: {list(all_cookies.keys())}")
    
    # Extract specific cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    test_cookie = request.cookies.get("test_cookie")
    
    # Also check for manual cookies
    access_token_manual = request.cookies.get("access_token_manual")
    refresh_token_manual = request.cookies.get("refresh_token_manual")
    
    logger.info(f"[DEV] access_token: {'present' if access_token else 'missing'}")
    logger.info(f"[DEV] refresh_token: {'present' if refresh_token else 'missing'}")
    logger.info(f"[DEV] test_cookie: {'present' if test_cookie else 'missing'}")
    logger.info(f"[DEV] access_token_manual: {'present' if access_token_manual else 'missing'}")
    logger.info(f"[DEV] refresh_token_manual: {'present' if refresh_token_manual else 'missing'}")
    
    # Create masked preview of tokens (first 6 + last 6 chars)
    def mask_token(token):
        if not token:
            return None
        if len(token) <= 12:
            return "***"
        return f"{token[:6]}...{token[-6:]}"
    
    access_token_preview = mask_token(access_token)
    refresh_token_preview = mask_token(refresh_token)
    
    # Determine overall authentication status
    authenticated = bool(access_token and refresh_token)
    
    logger.info(f"[DEV] Authentication status: {authenticated}")
    logger.info(f"[DEV] Access token preview: {access_token_preview}")
    logger.info(f"[DEV] Refresh token preview: {refresh_token_preview}")
    logger.info("[DEV] === COOKIE CHECK COMPLETE ===")
    
    return CookieCheckResponse(
        authenticated=authenticated,
        access_token_present=bool(access_token),
        refresh_token_present=bool(refresh_token),
        test_cookie_present=bool(test_cookie),
        access_token_preview=access_token_preview,
        refresh_token_preview=refresh_token_preview,
        test_cookie_value=test_cookie,
        all_cookies=all_cookies,
        request_cookie_header=cookie_header if cookie_header else None
    )
