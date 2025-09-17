


# Prereqs
import logging
logger = logging.getLogger() 


print(f"Root logger level: {logging.getLogger().getEffectiveLevel()}")
from fastapi import APIRouter, Depends, HTTPException, Form, Request, Response, Cookie
router = APIRouter(tags=["auth"])

from app.common.config import Config # To be passed to the use cases for static variable retrieval


from app.common.cookie_helper import set_auth_cookies, clear_auth_cookies # Making sure the cookies are consistent across the application

from app.interfaces.keyvalue.token_data_object import UserToken

# Interfaces
from app.interfaces.relationaldb.relationaldb_repo import RelationalRepository
from app.interfaces.keyvalue.keyvalue_repo import KeyValueRepository
from app.interfaces.user_notification.user_notification_repo import Notifier

# Use Cases
from app.application.use_case.auth_response import AuthResponse
from app.application.use_case.login import login as login_use_case
from app.application.use_case.refresh_token import refresh as refresh_use_case
from app.application.use_case.get_user_from_token import get_user_from_token
from app.application.use_case.forgot_password import forgot_password as forgot_password_use_case
from app.application.use_case.reset_password import reset_password as reset_password_use_case



def get_router(relational_db_adapter, key_value_adapter, config: Config, user_notification_adapter) -> APIRouter:
    def get_relational_adapter() -> RelationalRepository:
        logger.debug("Injecting relational_db_adapter: %s", relational_db_adapter)
        return relational_db_adapter

    def get_keyvalue_adapter() -> KeyValueRepository:
        logger.debug("Injecting key_value_adapter: %s", key_value_adapter)
        return key_value_adapter

    def get_config() -> Config:
        logger.debug("Injecting config: %s", config)
        return config
    
    def get_notification_adapter() -> Notifier:
        logger.debug("Injecting notification_adapter: %s", user_notification_adapter)
        return user_notification_adapter

    @router.post("/register")
    async def register(
        request: Request,
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Register endpoint called with email: %s", email)

        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = "web_browser"

        try:
            from app.application.use_case.register import register as register_use_case

            auth_response = await register_use_case(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id,
                database_adapter=repo,
                keyvalue_adapter=kv,
                config=config,
                AuthResponse=AuthResponse
            )
        except Exception as e:
            logger.exception("Error during registration for email %s: %s", email, str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        if auth_response.error:
            logger.warning("Registration failed for email %s: %s", email, auth_response.error)
            raise HTTPException(status_code=400, detail=auth_response.error)

        logger.info("Registration successful for email: %s", email)
        set_auth_cookies(response, auth_response.tokens["access_token"], auth_response.tokens["refresh_token"])
        return auth_response.to_dict()


    @router.post("/login")
    async def login(
        request: Request,
        response: Response,
        email: str = Form(...),
        password: str = Form(...),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Login endpoint called with email: %s", email)
        logger.debug("Received dependencies - repo: %s, kv: %s, config: %s", repo, kv, config)

        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = "web_browser"

        try:
            logger.debug("Calling login_use_case with email: %s", email)
            auth_response = await login_use_case(
                email=email,
                password=password,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id,
                database_adapter=repo,
                keyvalue_adapter=kv,
                config=config,
                AuthResponse=AuthResponse
            )
            logger.debug("login_use_case returned: %s", auth_response)

        except Exception as e:
            logger.exception("Unexpected error during login for email %s: %s", email, str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        if auth_response.error:
            logger.warning("Login failed for email %s: %s", email, auth_response.error)
            raise HTTPException(status_code=401, detail="Invalid email or password")

        logger.info("Login successful for email: %s", email)

        set_auth_cookies(response, auth_response.tokens["access_token"], auth_response.tokens["refresh_token"])
        return auth_response.to_dict()
    

    
    @router.post("/refresh")
    async def refresh(
        request: Request,
        response: Response,
        refresh_token: str = Cookie(None),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Refresh endpoint called")

        if not refresh_token:
            logger.warning("Refresh token missing in cookie")
            raise HTTPException(status_code=401, detail="Missing refresh token")

        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = "web_browser"

        try:
            auth_response = await refresh_use_case(
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id,
                database_adapter=repo,
                keyvalue_adapter=kv,
                config=config,
                AuthResponse=AuthResponse
            )
        except Exception as e:
            logger.exception("Unexpected error during token refresh: %s", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        if auth_response.error:
            logger.warning("Token refresh failed: %s", auth_response.error)
            raise HTTPException(status_code=401, detail=auth_response.error)

        logger.info("Token refresh successful for user %s", auth_response.user["id"])

        set_auth_cookies(response, auth_response.tokens["access_token"], auth_response.tokens["refresh_token"])
        return auth_response.to_dict()
    
    @router.get("/me")
    async def me(
        request: Request,
        access_token: str = Cookie(None),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Me endpoint called")

        if not access_token:
            logger.warning("Access token missing in cookie")
            raise HTTPException(status_code=401, detail="Missing access token")

        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = "web_browser"

        try:
            

            auth_response = await get_user_from_token(
                access_token=access_token,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id,
                database_adapter=repo,
                keyvalue_adapter=kv,
                config=config
            )
        except Exception as e:
            logger.exception("Unexpected error during /me: %s", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        if auth_response.error:
            logger.warning("Token verification failed: %s", auth_response.error)
            raise HTTPException(status_code=401, detail=auth_response.error)

        return auth_response.to_dict()
    
    @router.post("/password/forgot")
    async def forgot_password(
        request: Request,
        email: str = Form(...),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        notifier: Notifier = Depends(get_notification_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Forgot password endpoint called for email: %s", email)

        try:
            await forgot_password_use_case(
                email=email,
                database_adapter=repo,
                keyvalue_adapter=kv,
                notifier=notifier,
                config=config
            )
        except Exception as e:
            logger.exception("Error in forgot_password_use_case: %s", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        return {"detail": "If your email exists, password reset instructions have been sent."}

    @router.post("/password/reset")
    async def reset_password(
        token: str = Form(...),
        new_password: str = Form(...),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config)
    ):
        logger.info("Reset password endpoint called")

        try:
            result = await reset_password_use_case(
                token=token,
                new_password=new_password,
                database_adapter=repo,
                keyvalue_adapter=kv,
                config=config
            )
        except Exception as e:
            logger.exception("Error in reset_password_use_case: %s", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")

        if not result.get("success"):
            logger.warning("Password reset failed: %s", result.get("message"))
            raise HTTPException(status_code=result.get("status_code", 400), detail=result.get("message"))

        logger.info("Password reset successful")
        return {"detail": result.get("message")}

    @router.get("/validate")
    async def validate(
        request: Request,
        access_token: str = Cookie(None),
        repo: RelationalRepository = Depends(get_relational_adapter),
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        config: Config = Depends(get_config),
    ):
        # Log method and URL
        logging.info(f"[validate] method={request.method} url={request.url}")

        # Log headers
        logging.info("[validate] headers:")
        for k, v in request.headers.items():
            logging.info(f"  {k}: {v}")

        # Log cookies
        logging.info("[validate] cookies:")
        for k, v in request.cookies.items():
            logging.info(f"  {k}: {v}")

        # Access token resolution
        if access_token:
            logging.info(f"[validate] access_token from cookie: {access_token}")
        else:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
                logging.info(f"[validate] access_token from Authorization header: {access_token}")
            else:
                logging.warning("[validate] No access token provided in cookie or Authorization header")
                raise HTTPException(status_code=401, detail="Missing access token")

        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = request.headers.get("X-Device-ID", "web_browser")

        logging.info(f"[validate] ip={ip_address}, user_agent={user_agent}, device_id={device_id}")

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
            logging.warning(f"[validate] auth failed: {auth_response.error}")
            raise HTTPException(status_code=auth_response.status_code, detail=auth_response.error or "User not found")

        logging.info(f"[validate] validated user_id={auth_response.user['id']}")
        return {"user_id": auth_response.user["id"]}


    @router.post("/logout")
    async def logout(
        request: Request,
        response: Response,
        kv: KeyValueRepository = Depends(get_keyvalue_adapter),
        access_token: str = Cookie(None),
        refresh_token: str = Cookie(None),
    ):
        """
        Revoke tokens in KV store and clear cookies.
        """
        ip_address = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "unknown")
        device_id = request.headers.get("X-Device-ID", "web_browser")

        try:
            if refresh_token:
                key = UserToken.create(
                    access_token="",
                    refresh_token=refresh_token,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_id=device_id,
                    session_id="logout",
                    expires_in=0,
                )
                await kv.delete_token(key)

            if access_token:
                key = UserToken.create(
                    access_token=access_token,
                    refresh_token="",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_id=device_id,
                    session_id="logout",
                    expires_in=0,
                )
                await kv.delete_token(key)
        except Exception as e:
            logger.warning("Failed to revoke tokens: %s", str(e))

        clear_auth_cookies(response)
        return {"detail": "Logged out"}
    
    return router