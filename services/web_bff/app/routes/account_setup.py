from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import httpx
import logging
import os
import urllib.parse

router = APIRouter(tags=["Account Setup"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("account_setup")

# Define the request models
class SignupRequest(BaseModel):
    """
    Request model for initial user signup - supports both self-signup and workspace invites.
    
    This model handles the first step of the user registration process where an email
    is registered and an activation code is generated and sent via email.
    """
    email: EmailStr = Field(..., description="User's email address to be activated")
    workspace_id: Optional[int] = Field(None, description="Optional workspace ID for workspace invitations")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "workspace_id": 12345
            }
        }

class ConfirmRequest(BaseModel):
    """
    Request model for confirming activation codes received via email.
    
    This model is used when users click the activation link in their email
    or manually enter the activation code.
    """
    code: str = Field(..., description="Activation code received via email", min_length=1, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "code": "ABC123XYZ789"
            }
        }

# Define the response models
class SignupResponse(BaseModel):
    """
    Response model for signup operations indicating whether email activation was initiated.
    
    The success field indicates whether the signup process was initiated successfully.
    The code field may contain debug information (should not be exposed in production).
    """
    success: bool = Field(..., description="Whether the signup process was initiated successfully")
    email_confirmation_status: str = Field(..., description="Status of email confirmation (confirmed|pending|failed)")
    code: Optional[str] = Field(None, description="Debug: activation code (for testing only - remove in production)")
    reason: Optional[str] = Field(None, description="Reason for failure if success is false")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "email_confirmation_status": "pending",
                "code": None,
                "reason": None
            }
        }

class ConfirmResponse(BaseModel):
    """
    Response model for activation code confirmation operations.
    
    This response indicates whether the provided activation code was valid and provides
    the associated email address and optional workspace information.
    """
    valid: bool = Field(..., description="Whether the activation code is valid")
    email: Optional[EmailStr] = Field(None, description="Email address associated with the code")
    workspace_id: Optional[int] = Field(None, description="Workspace ID if this was a workspace invitation")

    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "email": "user@example.com",
                "workspace_id": 12345
            }
        }

class StatusResponse(BaseModel):
    """
    Response model for checking the status of an email signup process.
    
    Provides comprehensive status information about the signup process for a given email.
    """
    status: str = Field(..., description="Current status of the signup (pending|confirmed|failed)")
    last_email_result: Optional[str] = Field(None, description="Result of the last email sending attempt")
    is_valid: Optional[bool] = Field(None, description="Whether the email format and domain are valid")
    email_confirmation_status: str = Field(..., description="Email confirmation status")

    class Config:
        schema_extra = {
            "example": {
                "status": "confirmed",
                "last_email_result": "sent",
                "is_valid": True,
                "email_confirmation_status": "confirmed"
            }
        }

class EmailsResponse(BaseModel):
    """
    Response model for listing all email signups (admin endpoint).
    
    Used for administrative purposes to view all signup attempts and their statuses.
    """
    emails: list[dict] = Field(..., description="List of all email signup records with their details")

    class Config:
        schema_extra = {
            "example": {
                "emails": [
                    {
                        "email": "user1@example.com",
                        "status": "confirmed",
                        "workspace_id": 12345,
                        "created_at": "2025-01-01T10:00:00Z"
                    },
                    {
                        "email": "user2@example.com", 
                        "status": "pending",
                        "workspace_id": None,
                        "created_at": "2025-01-01T11:00:00Z"
                    }
                ]
            }
        }

class EmailForCodeResponse(BaseModel):
    """
    Response model for retrieving email information by activation code.
    
    Used to look up which email address is associated with a given activation code.
    """
    email: Optional[EmailStr] = Field(None, description="Email address associated with the activation code")
    workspace_id: Optional[int] = Field(None, description="Workspace ID if this was a workspace invitation")
    valid: bool = Field(..., description="Whether the code exists and is valid")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "workspace_id": 12345,
                "valid": True
            }
        }

class DevGetCodeResponse(BaseModel):
    """
    Response model for dev-only endpoint to retrieve activation codes.
    
    Only available in development mode for testing purposes.
    """
    email: EmailStr = Field(..., description="Email address that was queried")
    code: Optional[str] = Field(None, description="Activation code if found")
    found: bool = Field(..., description="Whether an activation code was found for this email")
    error: Optional[str] = Field(None, description="Error message if request failed")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "code": "ABC123XYZ789",
                "found": True,
                "error": None
            }
        }

SETUP_SERVICE_URL = "http://account_service:8000/"

@router.post("/signup", response_model=SignupResponse, summary="Initiate user signup process", description="""
This endpoint initiates the user signup process by validating the email and generating an activation code.

**Process Flow:**
1. Receives email address and optional workspace_id
2. Forwards request to setup microservice for email validation and code generation
3. Setup microservice checks if email is already confirmed
4. If not confirmed, generates new activation code and sends via email
5. Returns status indicating whether user should proceed to login or check email

**Input Options:**
- **Self Signup**: Provide email only (workspace_id = null)
- **Workspace Invite**: Provide email and workspace_id

**Response Scenarios:**
- **Already Confirmed**: User should be directed to login page
- **New/Pending**: User should check email for activation link

**Used By:**
- Frontend signup forms (/signup page)
- Workspace admin invite systems
""")
async def signup(request: SignupRequest):
    """
    Handles user signup by validating the email and generating a signup code.

    - **email**: The email address of the user to sign up.
    - **workspace_id**: Optional workspace ID for workspace invitations.
    """
    logger.info(f"[WEB-BFF] Outgoing API Request: POST {SETUP_SERVICE_URL}signup with payload: {request.dict()}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{SETUP_SERVICE_URL}signup", json=request.dict())

        logger.info(f"[WEB-BFF] API Response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            result = response.json()
            # Ensure we return the proper response format with email_confirmation_status
            return SignupResponse(
                success=result.get("success", True),
                email_confirmation_status=result.get("email_confirmation_status", "pending"),
                code=result.get("code"),  # For debugging only
                reason=result.get("reason")
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during signup API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with setup_service: {str(e)}")

@router.post("/confirm", response_model=ConfirmResponse, summary="Confirm activation code", description="""
This endpoint confirms an activation code received via email and activates the user's email address.

**Process Flow:**
1. Receives activation code from user (via link click or manual entry)
2. Forwards code to setup microservice for validation
3. Setup microservice validates code and activates email if valid
4. Returns email address and workspace information associated with the code

**Frontend Integration:**
- Called when user visits /setup?code=ACTIVATION_CODE
- Response determines next steps in user setup flow

**Response Data:**
- **valid**: Whether the code is valid and email is now activated
- **email**: The email address that was activated
- **workspace_id**: Workspace ID if this was a workspace invitation
""")
async def confirm(request: ConfirmRequest):
    """
    Confirms a signup code and updates the user's status.

    - **code**: The signup code to confirm.
    """
    logger.info(f"[WEB-BFF] Outgoing API Request: POST {SETUP_SERVICE_URL}confirm with payload: {request.dict()}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{SETUP_SERVICE_URL}confirm", json=request.dict())

        logger.info(f"[WEB-BFF] API Response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            result = response.json()
            # Map backend response fields to our response model
            is_valid = result.get("success", False) or result.get("valid", False)
            return ConfirmResponse(
                valid=is_valid,
                email=result.get("email"),
                workspace_id=result.get("workspace_id")
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during confirm API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with setup_service: {str(e)}")

@router.get("/status/{email}", response_model=StatusResponse, summary="Get email signup status", description="""
This endpoint retrieves the current signup status for a given email address.

**Use Cases:**
- Check if email is already confirmed (for login redirection)
- Monitor signup progress for debugging
- Verify email validity before proceeding with signup

**Status Values:**
- **pending**: Email signup initiated, awaiting activation
- **confirmed**: Email has been activated, user can proceed
- **failed**: Signup failed due to invalid email or other issues

**Admin Usage:**
This endpoint can be used by administrators to check the status of user signups
and troubleshoot activation issues.
""")
async def status(email: EmailStr):
    """
    Retrieves the signup status of a user by email.

    - **email**: The email address of the user to check the status for.
    """
    logger.info(f"[WEB-BFF] Outgoing API Request: GET {SETUP_SERVICE_URL}status/{email}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SETUP_SERVICE_URL}status/{email}")

        logger.info(f"[WEB-BFF] API Response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            result = response.json()
            return StatusResponse(
                status=result.get("status", "unknown"),
                last_email_result=result.get("last_email_result"),
                is_valid=result.get("is_valid"),
                email_confirmation_status=result.get("email_confirmation_status", result.get("status", "unknown"))
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during status API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with setup_service: {str(e)}")

@router.get("/emails", response_model=EmailsResponse, summary="List all email signups (Admin)", description="""
This endpoint returns a comprehensive list of all email signups in the system.

**Administrative Endpoint:**
This endpoint is intended for internal/administrative use only and should be protected
by appropriate authentication and authorization mechanisms in production.

**Response Data:**
Returns detailed information about all signup attempts including:
- Email addresses and their current status
- Associated workspace IDs for workspace invitations  
- Timestamp information for signup tracking
- Email sending results and validation status

**Security Note:**
This endpoint exposes sensitive user data and should be restricted to administrators only.
Consider implementing proper access controls before deploying to production.
""")
async def emails():
    """
    Retrieves a list of all email signups.
    """
    logger.info(f"[WEB-BFF] Outgoing API Request: GET {SETUP_SERVICE_URL}emails")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SETUP_SERVICE_URL}emails")

        logger.info(f"[WEB-BFF] API Response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return {"emails": response.json()}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during emails API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with setup_service: {str(e)}")

@router.get("/email-for-code/{code}", response_model=EmailForCodeResponse, summary="Retrieve email by activation code", description="""
This endpoint retrieves the email address and associated information for a given activation code.

**Use Cases:**
- Validate activation codes before processing
- Look up user information during the activation flow
- Debug activation issues by checking code-to-email mappings

**Security Considerations:**
- Activation codes should be treated as temporary secrets
- This endpoint should validate code expiration
- Consider rate limiting to prevent code enumeration attacks

**Response Information:**
- **email**: The email address associated with the activation code
- **workspace_id**: Workspace ID if this was a workspace invitation
- **valid**: Whether the code exists and is still valid (not expired)
""")
async def email_for_code(code: str):
    """
    Retrieves an email address by its signup code.

    - **code**: The signup code to retrieve the email for.
    """
    logger.info(f"[WEB-BFF] Outgoing API Request: GET {SETUP_SERVICE_URL}email-for-code/{code}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SETUP_SERVICE_URL}email-for-code/{code}")

        logger.info(f"[WEB-BFF] API Response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            result = response.json()
            return EmailForCodeResponse(
                email=result.get("email"),
                workspace_id=result.get("workspace_id"),
                valid=True
            )
        elif response.status_code == 404:
            return EmailForCodeResponse(
                email=None,
                workspace_id=None,
                valid=False
            )
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during email-for-code API request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with setup_service: {str(e)}")

@router.get("/dev/get-code/{email}", response_model=DevGetCodeResponse, summary="Get activation code for email (Dev Only)", description="""
This endpoint retrieves the activation code for a given email address by calling the account setup microservice's dev-only endpoint.

**Development Mode Only:**
This endpoint is only available when the web-bff environment is set to development mode (ENV=dev).
It will return a 404 error in production environments. The target microservice must also be running 
in development mode for its dev endpoints to be available.

**Use Cases:**
- Testing and development workflows
- Automated testing that needs to retrieve activation codes
- Development debugging and verification

**Security:**
This endpoint exposes sensitive activation codes and should NEVER be available in production.
Both the web-bff and the target microservice include built-in protection to only work in development environments.

**URL Encoding:**
The email parameter must be properly URL encoded. For example:
- user@example.com becomes user%40example.com
- user+test@example.com becomes user%2Btest%40example.com
""")
async def dev_get_code(email: str):
    """
    Retrieves the activation code for an email address - DEV MODE ONLY.

    - **email**: The URL-encoded email address to get the activation code for.
    
    This endpoint only works in development mode (ENV=dev).
    """
    # Check if we're in development mode
    if os.getenv("ENV", "dev").lower() != "dev":
        logger.warning(f"[WEB-BFF] Dev endpoint accessed in non-dev environment")
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    try:
        # URL decode the email parameter
        decoded_email = urllib.parse.unquote(email)
        logger.info(f"[WEB-BFF] Dev request: getting code for email {decoded_email}")
        
        # Validate that it's a proper email format
        try:
            # Basic email validation using pydantic
            from pydantic import validate_email
            validated_email = validate_email(decoded_email)[1]
        except ValueError as e:
            logger.error(f"[WEB-BFF] Invalid email format: {decoded_email}")
            return DevGetCodeResponse(
                email=decoded_email,
                code=None,
                found=False,
                error=f"Invalid email format: {str(e)}"
            )
        
        # Make request to the dev-only endpoint on the account setup microservice
        # Use host.docker.internal to reach the host machine from inside Docker container
        account_service_dev_url = f"http://host.docker.internal:8601/dev/get-code/{urllib.parse.quote(decoded_email, safe='')}"
        logger.info(f"[WEB-BFF] Outgoing API Request: GET {account_service_dev_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(account_service_dev_url)

        logger.info(f"[WEB-BFF] Account service API Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            code = result.get("code")
            return DevGetCodeResponse(
                email=validated_email,
                code=code,
                found=code is not None,
                error=None
            )
        elif response.status_code == 404:
            return DevGetCodeResponse(
                email=validated_email,
                code=None,
                found=False,
                error="No activation code found for this email"
            )
        else:
            logger.error(f"[WEB-BFF] Account service dev endpoint error: {response.status_code} - {response.text}")
            return DevGetCodeResponse(
                email=validated_email,
                code=None,
                found=False,
                error=f"Account service error: {response.text}"
            )

    except httpx.RequestError as e:
        logger.error(f"[WEB-BFF] Error during account service dev endpoint request: {str(e)}")
        return DevGetCodeResponse(
            email=email,  # Use original email since decoding might have failed
            code=None,
            found=False,
            error=f"Error communicating with account service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[WEB-BFF] Unexpected error in dev get-code endpoint: {str(e)}")
        return DevGetCodeResponse(
            email=email,  # Use original email since decoding might have failed
            code=None,
            found=False,
            error=f"Unexpected error: {str(e)}"
        )
