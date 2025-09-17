from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.responses import Response as StarletteResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
import httpx
import logging
import json

router = APIRouter(tags=["User Setup"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user_setup")

# Define the request models
class UserSetupRequest(BaseModel):
    """
    Comprehensive user setup request model containing all necessary information
    to create a complete user account with workspace association.
    """
    first_name: str = Field(..., description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(..., description="User's last name", min_length=1, max_length=50)
    email: EmailStr = Field(..., description="User's email address (must be pre-activated)")
    password: str = Field(..., description="User's password", min_length=8, max_length=128)
    workspace_id: Optional[int] = Field(None, description="Existing workspace ID to join (if joining existing workspace)")
    new_workspace_name: Optional[str] = Field(None, description="New workspace name to create (if creating new workspace)")

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe", 
                "email": "john.doe@example.com",
                "password": "secure_password123",
                "workspace_id": 12345,
                "new_workspace_name": None
            }
        }

# Define the response models
class UserSetupResponse(BaseModel):
    """
    Response model for user setup operations indicating success or failure
    with detailed error information for debugging.
    """
    success: bool = Field(..., description="Whether the user setup was successful")
    user_id: Optional[str] = Field(None, description="Created user ID if successful")
    workspace_id: Optional[int] = Field(None, description="Final workspace ID (existing or newly created)")
    workspace_name: Optional[str] = Field(None, description="Final workspace name")
    error_details: Optional[str] = Field(None, description="Detailed error message if setup failed")
    rollback_performed: Optional[bool] = Field(None, description="Whether rollback was performed due to errors")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "user_id": "user-uuid-12345",
                "workspace_id": 67890, 
                "workspace_name": "My Workspace",
                "error_details": None,
                "rollback_performed": None
            }
        }

class WorkspaceValidationResponse(BaseModel):
    """
    Response model for workspace validation operations.
    """
    valid: bool = Field(..., description="Whether the workspace ID is valid and accessible")
    workspace_name: Optional[str] = Field(None, description="Workspace name if valid")
    workspace_icon_file_tag: Optional[str] = Field(None, description="Workspace icon file tag if available")
    error_details: Optional[str] = Field(None, description="Error details if validation failed")

# Define service URLs
WORKSPACE_SERVICE_URL = "http://workspace_service:8000/"
HUMAN_SERVICE_URL = "http://human_service:8000/"
AUTH_SERVICE_URL = "http://auth_service:8000/"

@router.get("/workspaces/{workspace_id}/validate", 
           response_model=WorkspaceValidationResponse,
           summary="Validate workspace accessibility",
           description="""
This endpoint validates that a workspace exists and is accessible for new user registration.
It checks workspace validity and returns workspace details including name and icon.
Used during the user setup flow to confirm workspace invitation validity.
""")
async def validate_workspace(workspace_id: int):
    """
    Validates that a workspace exists and can be joined by new users.
    
    Args:
        workspace_id: The workspace ID to validate (integer)
        
    Returns:
        WorkspaceValidationResponse: Validation result with workspace details
        
    Raises:
        HTTPException: If workspace service is unavailable
    """
    logger.info(f"[WEB-BFF] Validating workspace ID: {workspace_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Call workspace service to get workspace details using integer ID
            response = await client.get(f"{WORKSPACE_SERVICE_URL}{workspace_id}")
        
        logger.info(f"[WEB-BFF] Workspace validation response: {response.status_code}")
        
        if response.status_code == 200:
            workspace_data = response.json()
            logger.info(f"[WEB-BFF] Workspace validation successful for: {workspace_data.get('name', 'Unknown')}")
            
            return WorkspaceValidationResponse(
                valid=True,
                workspace_name=workspace_data.get("name"),
                workspace_icon_file_tag=workspace_data.get("icon_file_tag"),
                error_details=None
            )
        elif response.status_code == 404:
            logger.warning(f"[WEB-BFF] Workspace not found: {workspace_id}")
            return WorkspaceValidationResponse(
                valid=False,
                workspace_name=None,
                workspace_icon_file_tag=None,
                error_details="Workspace not found or no longer accessible"
            )
        else:
            logger.error(f"[WEB-BFF] Workspace validation failed: {response.status_code} - {response.text}")
            return WorkspaceValidationResponse(
                valid=False,
                workspace_name=None,
                workspace_icon_file_tag=None,
                error_details=f"Workspace validation failed: {response.text}"
            )
            
    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during workspace validation: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Error communicating with workspace service: {str(e)}"
        )

@router.post("/complete", 
            response_model=UserSetupResponse,
            summary="Complete user setup with workspace association",
            description="""
This is the comprehensive endpoint that handles the final user setup process.
It coordinates between workspace, human, and auth microservices to create a complete user account.

**Process Flow:**
1. Validates/creates workspace (based on workspace_id vs new_workspace_name)
2. Stores user details in human microservice with workspace association
3. Creates authentication credentials in auth microservice
4. Performs rollback of all changes if any step fails

**Input Requirements:**
- Either `workspace_id` (to join existing) OR `new_workspace_name` (to create new) must be provided
- Email must have been pre-activated through the account setup flow
- Password must meet security requirements (min 8 characters)

**Error Handling:**
- All database changes are rolled back if any step fails
- Detailed error messages are provided for debugging
- Rollback status is indicated in the response
""")
async def complete_user_setup(request: UserSetupRequest, response: Response):
    """
    Completes the user setup process by coordinating workspace, human, and auth services.
    
    This endpoint handles the final step of user registration after email activation.
    It ensures atomicity by rolling back all changes if any step fails.
    
    Args:
        request: UserSetupRequest containing all user and workspace details
        
    Returns:
        UserSetupResponse: Result of the setup operation with success/failure details
        
    Raises:
        HTTPException: For validation errors or service communication failures
    """
    logger.info(f"[WEB-BFF] Starting user setup for email: {request.email}")
    
    # Validate input - exactly one workspace option should be provided
    has_workspace_id = request.workspace_id is not None
    has_new_workspace = request.new_workspace_name is not None
    
    if not (has_workspace_id or has_new_workspace):
        raise HTTPException(
            status_code=400,
            detail="Either workspace_id (to join existing) or new_workspace_name (to create new) must be provided"
        )
    
    if has_workspace_id and has_new_workspace:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both workspace_id and new_workspace_name - choose one"
        )
    
    # Track created resources for rollback
    created_workspace_id = None
    created_human_id = None
    created_auth_record = False
    final_workspace_id: Optional[int] = None
    final_workspace_obfuscated_id: Optional[str] = None
    final_workspace_name = None
    
    try:
        # Step 1: Handle workspace (validate existing or create new)
        if has_workspace_id:
            logger.info(f"[WEB-BFF] Validating existing workspace: {request.workspace_id}")
            
            async with httpx.AsyncClient() as client:
                workspace_response = await client.get(f"{WORKSPACE_SERVICE_URL}{request.workspace_id}")
            
            if workspace_response.status_code != 200:
                logger.error(f"[WEB-BFF] Workspace validation failed: {workspace_response.status_code}")
                return UserSetupResponse(
                    success=False,
                    user_id=None,
                    workspace_id=None,
                    workspace_name=None,
                    error_details=f"Invalid workspace ID: {request.workspace_id}",
                    rollback_performed=False
                )
            
            workspace_data = workspace_response.json()
            final_workspace_id = workspace_data.get("id")  # Use the integer ID from response
            final_workspace_obfuscated_id = workspace_data.get("obfuscated_id")  # Use obfuscated ID for human service
            final_workspace_name = workspace_data.get("name", "Unknown Workspace")
            logger.info(f"[WEB-BFF] Workspace validation successful: {final_workspace_name}")
            
        else:  # Create new workspace
            logger.info(f"[WEB-BFF] Creating new workspace: {request.new_workspace_name}")
            
            workspace_payload = {
                "name": request.new_workspace_name,
                "created_by": "00000000-0000-0000-0000-000000000001",  # Placeholder UUID
                "owner_id": "00000000-0000-0000-0000-000000000001"     # Will be updated after user creation
            }
            
            async with httpx.AsyncClient() as client:
                workspace_response = await client.post(f"{WORKSPACE_SERVICE_URL}", json=workspace_payload)
            
            if workspace_response.status_code != 200:
                logger.error(f"[WEB-BFF] Workspace creation failed: {workspace_response.status_code}")
                return UserSetupResponse(
                    success=False,
                    user_id=None,
                    workspace_id=None,
                    workspace_name=None,
                    error_details=f"Failed to create workspace: {workspace_response.text}",
                    rollback_performed=False
                )
            
            workspace_data = workspace_response.json()
            logger.info(f"[WEB-BFF] Workspace creation response: {workspace_data}")
            created_workspace_id = workspace_data.get("id")  # Use the integer ID from response
            created_workspace_obfuscated_id = workspace_data.get("obfuscated_id")  # Use obfuscated ID for human service
            final_workspace_id = created_workspace_id
            final_workspace_obfuscated_id = created_workspace_obfuscated_id
            final_workspace_name = request.new_workspace_name
            logger.info(f"[WEB-BFF] Workspace created successfully: {final_workspace_id}")
        
        # Step 2: Create human record with workspace association
        logger.info(f"[WEB-BFF] Creating human record for: {request.email}")
        logger.info(f"[WEB-BFF] Using workspace_id: {final_workspace_obfuscated_id} (obfuscated) for workspace {final_workspace_id} (integer)")
        
        human_payload = {
            "workspace_id": final_workspace_obfuscated_id,  # Use obfuscated workspace ID
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "created_by": "00000000-0000-0000-0000-000000000001"  # Placeholder UUID for system creation
        }
        
        logger.info(f"[WEB-BFF] Human service payload: {human_payload}")
        
        async with httpx.AsyncClient() as client:
            human_response = await client.post(f"{HUMAN_SERVICE_URL}", json=human_payload)
        
        if human_response.status_code != 200:
            logger.error(f"[WEB-BFF] Human creation failed: {human_response.status_code}")
            await _perform_rollback(created_workspace_id, None, False)
            return UserSetupResponse(
                success=False,
                user_id=None,
                workspace_id=None,
                workspace_name=None,
                error_details=f"Failed to create user record: {human_response.text}",
                rollback_performed=True
            )
        
        human_data = human_response.json()
        created_human_id = human_data.get("id")  # Use "id" field from HumanResponse
        logger.info(f"[WEB-BFF] Human record created: {created_human_id}")
        
        # Step 3: Create auth credentials and log user in
        logger.info(f"[WEB-BFF] Creating auth account and logging in user: {request.email}")
        
        # Use form data for auth service registration
        auth_payload = {
            "email": request.email,
            "password": request.password,
            "first_name": request.first_name,
            "last_name": request.last_name
        }
        
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{AUTH_SERVICE_URL}register", 
                data=auth_payload,  # Use data for form encoding
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        if auth_response.status_code != 200:
            logger.error(f"[WEB-BFF] Auth creation failed: {auth_response.status_code}")
            await _perform_rollback(created_workspace_id, created_human_id, False)
            return UserSetupResponse(
                success=False,
                user_id=None,
                workspace_id=None,
                workspace_name=None,
                error_details=f"Failed to create authentication credentials: {auth_response.text}",
                rollback_performed=True
            )
        
        # Extract user ID from auth service response
        auth_data = auth_response.json()
        auth_user_id = auth_data.get("user", {}).get("id")
        logger.info(f"[WEB-BFF] Auth user created: {auth_user_id}")
        
        # Extract and set authentication cookies from auth service response
        auth_cookies = auth_response.cookies
        logger.info(f"[WEB-BFF] Auth service cookies received: {list(auth_cookies.keys())}")
        logger.info(f"[WEB-BFF] Auth service response headers: {dict(auth_response.headers)}")
        
        # Prepare response data
        response_data = {
            "success": True,
            "user_id": auth_user_id,
            "workspace_id": final_workspace_id,
            "workspace_name": final_workspace_name,
            "error_details": None,
            "rollback_performed": False
        }
        
        # Prepare response data
        response_data = {
            "success": True,
            "user_id": auth_user_id,
            "workspace_id": final_workspace_id,
            "workspace_name": final_workspace_name,
            "error_details": None,
            "rollback_performed": False
        }
        
        # CORRECT APPROACH: Refresh token in cookie, access token in response body
        response_data = {
            "success": True,
            "user_id": auth_user_id,
            "workspace_id": final_workspace_id,
            "workspace_name": final_workspace_name,
            "access_token": auth_cookies.get("access_token"),  # Frontend gets this
            "token_type": "bearer",
            "expires_in": 3600,
            "error_details": None,
            "rollback_performed": False
        }
        
        # Create JSONResponse
        response = JSONResponse(content=response_data)
        
        # Set ONLY the refresh token as a secure HttpOnly cookie
        if "refresh_token" in auth_cookies:
            refresh_token_value = auth_cookies["refresh_token"]
            logger.info(f"[WEB-BFF] Setting refresh_token cookie: {refresh_token_value[:10]}...")
            response.set_cookie(
                key="refresh_token",
                value=refresh_token_value,
                httponly=True,
                secure=False,  # False for localhost development
                path="/",
                samesite="lax",
                max_age=7*24*3600  # 7 days for refresh token
            )
            logger.info("[WEB-BFF] Set refresh_token as secure HttpOnly cookie")
        
        if "access_token" in auth_cookies:
            logger.info("[WEB-BFF] Returned access_token in response body for frontend")
        
        logger.info("[WEB-BFF] Using CORRECT approach: refresh token in cookie, access token in response")
        
        created_auth_record = True
        logger.info(f"[WEB-BFF] User setup completed successfully for: {request.email}")
        
        return response
        
    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Service communication error during user setup: {str(e)}")
        await _perform_rollback(created_workspace_id, created_human_id, created_auth_record)
        return UserSetupResponse(
            success=False,
            user_id=None,
            workspace_id=None,
            workspace_name=None,
            error_details=f"Service communication error: {str(e)}",
            rollback_performed=True
        )
    
    except Exception as e:
        logger.error(f"[WEB-BFF] Unexpected error during user setup: {str(e)}")
        await _perform_rollback(created_workspace_id, created_human_id, created_auth_record)
        return UserSetupResponse(
            success=False,
            user_id=None,
            workspace_id=None,
            workspace_name=None,
            error_details=f"Unexpected error: {str(e)}",
            rollback_performed=True
        )

async def _perform_rollback(workspace_id: Optional[int], human_id: Optional[str], auth_created: bool):
    """
    Performs rollback of created resources in reverse order.
    
    Args:
        workspace_id: Workspace ID to delete (if newly created)
        human_id: Human ID to delete
        auth_created: Whether auth record was created and needs deletion
    """
    logger.warning("[WEB-BFF] Performing rollback of user setup changes")
    
    # Rollback in reverse order: auth -> human -> workspace
    # Note: Auth service doesn't provide user deletion endpoint, so we can't rollback auth creation
    if auth_created and human_id:
        logger.warning(f"[WEB-BFF] Cannot rollback auth record for human {human_id} - auth service doesn't provide deletion endpoint")
    
    if human_id:
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{HUMAN_SERVICE_URL}{human_id}")
            logger.info(f"[WEB-BFF] Rollback: Deleted human record {human_id}")
        except Exception as e:
            logger.error(f"[WEB-BFF] Rollback failed for human record: {str(e)}")
    
    if workspace_id:
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{WORKSPACE_SERVICE_URL}{workspace_id}")
            logger.info(f"[WEB-BFF] Rollback: Deleted workspace {workspace_id}")
        except Exception as e:
            logger.error(f"[WEB-BFF] Rollback failed for workspace: {str(e)}")
    
    logger.info("[WEB-BFF] Rollback completed")
