import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes.routes import get_location_router
from app.interfaces.relationaldb.postgres_adapter import PostGresAdapter
from app.models.location import Location
from app.models.base import Base
from app.dev.dev_seed import seed_location

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(asctime)s:%(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Starting FastAPI application for service 'location'")



# ---- DB Table Init via Adapter ----
def init_location_table(adapter: PostGresAdapter):
    engine = adapter.db.get_bind()
    from app.utils.wait_for_db import wait_for_db
    wait_for_db(engine)
    if os.getenv("ENV", "").lower() == "dev":
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped for dev mode")
    Base.metadata.create_all(bind=engine, tables=[Location.__table__])
    logger.info("Location table initialized via PostGresAdapter")


class SQLAlchemySessionRollbackMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_adapter):
        super().__init__(app)
        self.db_adapter = db_adapter

    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Rollback the session on any unhandled exception
            try:
                self.db_adapter.db.rollback()
                logger.warning("Session rollback performed due to exception.")
            except Exception as rollback_exc:
                logger.error(f"Failed to rollback session: {rollback_exc}")
            raise


# ---- App Setup ----
relational_db = PostGresAdapter()
init_location_table(relational_db)

logger.info("Initialized PostGresAdapter for 'location'")

app = FastAPI()
logger.info("FastAPI app instance created")

# ---- Add SQLAlchemy rollback middleware ----
app.add_middleware(SQLAlchemySessionRollbackMiddleware, db_adapter=relational_db)


# ---- Exception Handlers ----

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail} | Path: {request.url.path}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error: {str(exc.orig)} | Path: {request.url.path}")
    detail = str(exc.orig).split("DETAIL:")[-1].strip() if "DETAIL:" in str(exc.orig) else "Data integrity error occurred."
    return JSONResponse(status_code=400, content={"error": f"Data conflict: {detail}"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error at {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on path {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred. Please try again or contact support."})


# ---- Router Mount ----

app.include_router(
    get_location_router(relational_db),
    tags=["location"]
)
logger.info("Router mounted with tag 'location' and no prefix")


# ---- Dev Init Hook ----

if os.getenv("ENV", "").lower() == "dev":
    logger.info("ENV=dev detected, initializing development data")
    seed_location(relational_db)
else:
    logger.info("Production mode")
