import logging
import os
from pathlib import Path

# Configure logging with file output for log aggregation
log_dir = Path("/app/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.FileHandler('/app/logs/web_bff.log'),
        logging.StreamHandler()  # Keep console output for development
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting Web BFF service with file logging enabled")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from starlette.middleware.base import BaseHTTPMiddleware

# from app.routes.views import router as views_router
from app.routes.views import router as views_router
from app.routes.auth import router as auth_router 
from app.routes.account_setup import router as account_setup_router
from app.routes.user_setup import router as user_setup_router
from app.routes.workspaces import router as workspaces_router
from app.routes.dev import router as dev_router

app = FastAPI()

# Open CORS and CSP policies for development
if os.getenv("ENV", "dev").lower() == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://app.ergolux.io.localhost:5173",
            "https://app.ergolux.io.localhost:5173"
        ],  # Add all dev frontend origins for credentials
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_csp_headers(request: Request, call_next):
        response = await call_next(request)
        # Open CSP policies for dev: allow everything
        response.headers["Content-Security-Policy"] = (
            "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;"
            "script-src * 'unsafe-inline' 'unsafe-eval' data: blob:;"
            "style-src * 'unsafe-inline' data: blob:;"
            "img-src * data: blob:;"
            "font-src * data:;"
            "connect-src *;"
            "frame-src *;"
        )
        return response

class LogRawRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        import json
        from fastapi.responses import JSONResponse
        from starlette.responses import StreamingResponse
        
        # Log incoming request
        body = await request.body()
        start_time = time.time()
        logging.info(f"RAW REQUEST: {request.method} {request.url} | Headers: {dict(request.headers)} | Body: {body!r}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        
        # Capture response body for logging - this is tricky with FastAPI
        response_body = "N/A"
        original_response = response
        
        try:
            # Check if it's a streaming response (which includes JSONResponse)
            body_iterator = getattr(response, 'body_iterator', None)
            if body_iterator is not None:
                # Collect all chunks from the stream
                body_chunks = []
                async for chunk in body_iterator:
                    if chunk:  # Only add non-empty chunks
                        body_chunks.append(chunk)
                
                if body_chunks:
                    # Reconstruct the full body
                    response_body_bytes = b''.join(body_chunks)
                    response_body = response_body_bytes.decode('utf-8', errors='ignore')
                    
                    # Create a new response with the same content to avoid consuming the original
                    from starlette.responses import Response
                    response = Response(
                        content=response_body_bytes,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=getattr(response, 'media_type', 'application/json')
                    )
            elif hasattr(response, 'body') and response.body is not None:
                # For non-streaming responses
                response_body_attr = getattr(response, 'body', None)
                if isinstance(response_body_attr, bytes):
                    response_body = response_body_attr.decode('utf-8', errors='ignore')
                elif isinstance(response_body_attr, str):
                    response_body = response_body_attr
                else:
                    response_body = str(response_body_attr)
                    
        except Exception as e:
            # If anything goes wrong, use the original response and log the error
            response = original_response
            response_body = f"[Error capturing response: {str(e)}]"
        
        # Try to format JSON for better readability
        try:
            if response_body and response_body not in ["N/A"] and isinstance(response_body, str):
                stripped = response_body.strip()
                if len(stripped) > 0 and (stripped[0] == '{' or stripped[0] == '['):
                    parsed_json = json.loads(response_body)
                    response_body = json.dumps(parsed_json, separators=(',', ':'))
        except (json.JSONDecodeError, TypeError):
            # Not JSON or can't parse, keep as is
            pass
        
        logging.info(f"RAW RESPONSE: {request.method} {request.url} | Status: {response.status_code} | Time: {process_time:.3f}s | Headers: {dict(response.headers)} | Body: {response_body}")
        
        return response

app.add_middleware(LogRawRequestMiddleware)

app.include_router(views_router)
app.include_router(auth_router)  
app.include_router(account_setup_router, prefix="/account-setup")
app.include_router(user_setup_router, prefix="/user-setup")
app.include_router(workspaces_router, prefix="/workspaces")

# Only include dev router in development mode
if os.getenv("ENV", "dev").lower() == "dev":
    app.include_router(dev_router)  # No prefix for dev routes

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "web-bff ok"}
