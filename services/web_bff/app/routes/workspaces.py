from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import httpx
import logging

router = APIRouter(tags=["Workspaces"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workspaces")

# Define the request model
class WorkspaceRequest(BaseModel):
    name: str

# Define the workspace response model for search
class WorkspaceItem(BaseModel):
    id: int  # Changed from str to int as the service returns numeric IDs
    name: str
    owner_id: str
    created_by: str
    created_at: str

class WorkspaceSearchResponse(BaseModel):
    results: List[WorkspaceItem]
    total: int
    limit: int
    offset: int

# Define the workspace service URL
WORKSPACE_SERVICE_URL = "http://workspace_service:8000/"

@router.get("/{workspace_id}/validate", 
           summary="Validate workspace for user signup",
           description="""
This endpoint validates that a workspace exists and is accessible for new user registration.
It's specifically designed for the user setup flow to verify workspace invitations.

**Use Cases:**
- Validate workspace invitation links before user signup
- Verify workspace accessibility during user setup process
- Get workspace details (name, icon) for invitation confirmation dialogs

**Response Information:**
- **exists**: Whether the workspace exists and is accessible
- **name**: Workspace name for display in confirmation dialogs
- **icon_file_tag**: Workspace icon file tag for UI display
- **error**: Error message if workspace is not accessible

**Integration:**
This endpoint is called during the user setup flow when a workspace_id is provided,
either from an invitation link or during the signup process.
""")
async def validate_workspace_for_signup(workspace_id: int):
    """
    Validates that a workspace exists and can be joined by new users.
    
    Args:
        workspace_id: The workspace ID to validate
        
    Returns:
        Workspace validation result with details for user setup flow
    """
    logger.info(f"[WEB-BFF] Validating workspace for signup: {workspace_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Use the existing search endpoint to find the workspace
            response = await client.get(f"{WORKSPACE_SERVICE_URL}", params={"workspace_id": workspace_id})
        
        logger.info(f"[WEB-BFF] Workspace validation response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get("results", [])
            
            # Check if workspace was found
            if workspaces and len(workspaces) > 0:
                workspace = workspaces[0]
                logger.info(f"[WEB-BFF] Workspace validation successful: {workspace.get('name')}")
                return {
                    "exists": True,
                    "name": workspace.get("name"),
                    "icon_file_tag": workspace.get("icon_file_tag"),
                    "error": None
                }
            else:
                logger.warning(f"[WEB-BFF] Workspace not found: {workspace_id}")
                return {
                    "exists": False,
                    "name": None,
                    "icon_file_tag": None,
                    "error": "Workspace not found or no longer accessible"
                }
        else:
            logger.error(f"[WEB-BFF] Workspace validation failed: {response.status_code}")
            return {
                "exists": False,
                "name": None,
                "icon_file_tag": None,
                "error": f"Failed to validate workspace: {response.text}"
            }
            
    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during workspace validation: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Error communicating with workspace service: {str(e)}"
        )

async def check_workspace_name_exists(name: str) -> bool:
    """
    Check if a workspace with the given name already exists.
    
    Args:
        name: The workspace name to check
        
    Returns:
        bool: True if the workspace name exists, False otherwise
    """
    logger.info(f"[WEB-BFF] Checking if workspace name '{name}' already exists")
    try:
        async with httpx.AsyncClient() as client:
            # Use the search endpoint with name filter
            response = await client.get(f"{WORKSPACE_SERVICE_URL}", params={"name": name})
        
        logger.info(f"[WEB-BFF] Workspace name check response: {response.status_code}")
        logger.debug(f"[WEB-BFF] Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"[WEB-BFF] Parsed response: {data}")
            # Check if any results were returned
            return data.get("total", 0) > 0 and len(data.get("results", [])) > 0
        else:
            logger.warning(f"[WEB-BFF] Failed to check workspace name, status code: {response.status_code}")
            # Default to assuming it doesn't exist if we can't check
            return False
    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error checking workspace name: {str(e)}")
        # Default to assuming it doesn't exist if we can't check
        return False

# Define the response model
class WorkspaceResponse(BaseModel):
    success: bool
    workspace_id: str | None = None
    reason: str | None = None

@router.get("", response_model=WorkspaceSearchResponse, summary="Search workspaces", description="""
This endpoint allows searching and listing workspaces. It supports filtering by name and pagination.
""")
async def search_workspaces(
    request: Request, 
    name: Optional[str] = Query(None, description="Filter workspaces by name"),
    limit: int = Query(20, description="Number of workspaces per page", ge=1, le=100),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """
    Search for workspaces with optional filtering and pagination.
    
    - **name**: Optional filter by workspace name (case-insensitive partial match)
    - **limit**: Maximum number of results to return (between 1 and 100)
    - **offset**: Number of results to skip (for pagination)
    """
    logger.info(f"[WEB-BFF] Received request to search workspaces with filters: name={name}, limit={limit}, offset={offset}")
    
    # Extract user ID from cookies
    user_id = request.cookies.get("user_id")
    if not user_id:
        # Using a fake UUID for now
        user_id = "00000000-0000-0000-0000-000000000001"
        logger.info(f"[WEB-BFF] Using fake user_id for workspace search: {user_id}")
    else:
        logger.info(f"[WEB-BFF] Extracted user_id from cookies for workspace search: {user_id}")
    
    # Construct query parameters
    params = {}
    if name:
        params["name"] = name
    params["limit"] = limit
    params["offset"] = offset
    
    try:
        logger.info(f"[WEB-BFF] Sending workspace search request to workspace_service with params: {params}")
        async with httpx.AsyncClient() as client:
            response = await client.get(WORKSPACE_SERVICE_URL, params=params)
        
        logger.info(f"[WEB-BFF] Received workspace search response: {response.status_code}")
        
        if response.status_code == 200:
            search_results = response.json()
            logger.info(f"[WEB-BFF] Workspace search successful, found {search_results.get('total', 0)} workspaces")
            logger.debug(f"[WEB-BFF] Raw search results: {search_results}")
            return search_results
        else:
            logger.warning(f"[WEB-BFF] Workspace search failed with status code {response.status_code}: {response.text}")
            return {
                "results": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
            
    except ValidationError as e:
        # This helps debug Pydantic validation errors
        logger.error(f"[WEB-BFF] Validation error during workspace search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {str(e)}")
            
    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during workspace search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with workspace_service: {str(e)}")

@router.post("", response_model=WorkspaceResponse, summary="Create a new workspace", description="""
This endpoint allows internal services to create a new workspace. The `owner_id` and `created_by` fields are populated from the user ID in the cookies.
""")
async def create_workspace(request: Request, workspace_request: WorkspaceRequest):
    """
    Handles workspace creation by sending a request to the workspace service.

    - **name**: The name of the workspace to create.
    """
    logger.info("[WEB-BFF] Received request to create a workspace")

    # Extract user ID from cookies or use a fake one for now
    user_id = request.cookies.get("user_id")
    if not user_id:
        # Using a fake UUID for now
        user_id = "00000000-0000-0000-0000-000000000001"
        logger.info(f"[WEB-BFF] Using fake user_id: {user_id}")
    else:
        logger.info(f"[WEB-BFF] Extracted user_id from cookies: {user_id}")
    
    # Check if workspace name already exists
    name_exists = await check_workspace_name_exists(workspace_request.name)
    if name_exists:
        logger.warning(f"[WEB-BFF] Workspace name '{workspace_request.name}' already exists")
        return {"success": False, "reason": "Workspace name must be unique"}

    # Construct the payload
    payload = {
        "name": workspace_request.name,
        "created_by": user_id,
        "owner_id": user_id
    }

    logger.info(f"[WEB-BFF] Constructed payload for workspace creation: {payload}")

    try:
        logger.info(f"[WEB-BFF] Sending API request to workspace_service at {WORKSPACE_SERVICE_URL}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{WORKSPACE_SERVICE_URL}", json=payload)

        logger.info(f"[WEB-BFF] Received response from workspace_service: {response.status_code} - {response.text}")
        if response.status_code == 200:
            logger.info("[WEB-BFF] Workspace creation successful")
            return response.json()
        else:
            logger.warning(f"[WEB-BFF] Workspace creation failed with status code {response.status_code}")
            # Get the response text first to avoid undefined variable issues
            error_text = response.text
            
            # Try to parse the error response
            import json
            try:
                # Check if the text is a JSON string
                try:
                    error_json = json.loads(error_text)
                    
                    # If it has an error field, extract it
                    if isinstance(error_json, dict) and "error" in error_json:
                        logger.info(f"[WEB-BFF] Extracted error message: {error_json['error']}")
                        return {"success": False, "reason": error_json["error"]}
                except json.JSONDecodeError:
                    # Not valid JSON, continue with other approaches
                    pass
                
                # If we're here, it could be a string that contains escaped JSON
                if "\"error\":" in error_text:
                    # Try to extract the error message using regex
                    import re
                    error_match = re.search(r'"error":"([^"]+)"', error_text)
                    if error_match:
                        error_message = error_match.group(1)
                        logger.info(f"[WEB-BFF] Extracted error message from regex: {error_message}")
                        return {"success": False, "reason": error_message}
            
            except Exception as e:
                logger.error(f"[WEB-BFF] Error parsing error response: {str(e)}")
            
            # If all else fails, return a clean generic error with the raw response
            return {"success": False, "reason": f"Request failed: {error_text}"}

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during workspace creation API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with workspace_service: {str(e)}")
