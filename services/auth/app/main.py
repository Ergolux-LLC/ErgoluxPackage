import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import asyncio
from contextlib import asynccontextmanager
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Literal
from sqlalchemy import text

from app.common import config as config_module
from app.infrastructure.routers.auth import get_router as get_auth_router
from app.infrastructure.routers.internal import internal_router
from app.interfaces.relationaldb.postgres_adapter import PostgresUserAdapter
from app.interfaces.keyvalue.redis_adapter import RedisAdapter
from app.interfaces.user_notification.email_notification_adapter import EmailNotifierAdapter

import time
from datetime import datetime, timezone

# Load config from .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
config = config_module.Config(env_path)



# Instantiate adapters
relational_db_adapter = PostgresUserAdapter(config)
keyvalue_adapter = RedisAdapter(config)
user_notification_adapter = EmailNotifierAdapter(config)

# Record when this service process started so /status can report uptime
SERVICE_START_TS = time.time()
SERVICE_STARTED_AT = datetime.now(timezone.utc).isoformat()

MAX_RETRIES = 5
RETRY_DELAY = 1  # seconds

async def retry_redis_check():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pong = await keyvalue_adapter._client.ping()
            if pong is True:
                logger.info("🟥 Redis is live and spicy")
                return
            raise Exception("Unexpected Redis ping response")
        except Exception as e:
            logger.warning("❌ Redis check failed (attempt %d/%d): %s", attempt, MAX_RETRIES, str(e))
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
            else:
                logger.error("🔥 Redis failed after %d attempts", MAX_RETRIES)
                raise

async def retry_postgres_check():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with relational_db_adapter.session.begin():
                relational_db_adapter.session.execute(text("SELECT 1"))
            logger.info("🐘 Postgres is standing strong and majestic")
            return
        except Exception as e:
            logger.warning("❌ Postgres check failed (attempt %d/%d): %s", attempt, MAX_RETRIES, str(e))
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
            else:
                logger.error("🔥 Postgres failed after %d attempts", MAX_RETRIES)
                raise

@asynccontextmanager
async def lifespan(app: FastAPI):

    
    logger.info("🔌 Booting up... ")



    await retry_redis_check()

    await retry_postgres_check()
    
    # Initialize database tables if needed
    try:
        from app.infrastructure.db.metadata import metadata
        bind = relational_db_adapter.session.get_bind()
        metadata.create_all(bind=bind)
        logger.info("🗄️ Database tables initialized")
    except Exception as e:
        logger.error("Failed to initialize database tables: %s", str(e))
        
    logger.info (config.get("ENVIRONMENT"))
    
    yield  # App is now ready

    logger.info("📦 Shutting down... cleaning up connections")

    try:
        await keyvalue_adapter._client.close()
        logger.info("🟥 Redis connection tucked into bed")
    except Exception as e:
        logger.warning("⚠️ Failed to close Redis: %s", str(e))

    try:
        relational_db_adapter.session.close()
        logger.info("🐘 Postgres session closed with honor")
    except Exception as e:
        logger.warning("⚠️ Failed to close Postgres session: %s", str(e))

    logger.info("👋 Server's going night-night. If you dream of segfaults, seek help. 🛌💤🦥")

# Set the global prefix to /api
app = FastAPI(lifespan=lifespan)

# Mount public-facing auth router
app.include_router(
    get_auth_router(relational_db_adapter, keyvalue_adapter, config, user_notification_adapter)
)

# Mount internal router (e.g., for /internal/validate)
app.include_router(internal_router)


@app.get("/status", response_model=dict)
async def status_check():
    """Service status endpoint. Checks Redis and Postgres connectivity and returns a summary.

    Returns 200 when both Redis and Postgres are responsive, otherwise 503.
    """
    results = {}

    # Check Redis
    try:
        pong = None
        try:
            pong = await keyvalue_adapter._client.ping()
        except Exception:
            # Some redis clients expose sync ping; try getattr fallback
            client = getattr(keyvalue_adapter, '_client', None)
            if client is not None and hasattr(client, 'ping'):
                pong = await client.ping()
        results['redis'] = 'ok' if pong is True else f'unexpected_response: {pong}'
    except Exception as e:
        results['redis'] = f'error: {str(e)}'

    # Check Postgres
    try:
        with relational_db_adapter.session.begin():
            relational_db_adapter.session.execute(text("SELECT 1"))
        results['postgres'] = 'ok'
    except Exception as e:
        results['postgres'] = f'error: {str(e)}'

    results['environment'] = config.get('ENVIRONMENT')

    # Service component: uptime and start time for the running auth service
    try:
        uptime_seconds = int(time.time() - SERVICE_START_TS)
        service_component = {
            'status': 'ok',
            'uptime_seconds': uptime_seconds,
            'started_at': SERVICE_STARTED_AT,
        }
    except Exception as e:
        service_component = {'status': 'error', 'detail': str(e)}

    overall_ok = results.get('redis') == 'ok' and results.get('postgres') == 'ok'
    status_code = 200 if overall_ok else 503

    # Build structured response
    class StatusComponent(BaseModel):
        status: Literal['ok', 'error']
        detail: str | None = None

    class StatusResponse(BaseModel):
        redis: StatusComponent
        postgres: StatusComponent
        service: dict
        environment: str | None = None

    from typing import Optional

    def make_component(value: Optional[str]):
        v = value if value is not None else 'error: unknown'
        if v == 'ok':
            return {'status': 'ok', 'detail': None}
        if isinstance(v, str) and v.startswith('error:'):
            return {'status': 'error', 'detail': v[len('error: '):]}
        return {'status': 'error', 'detail': str(v)}

    body = {
        'redis': make_component(results.get('redis')),
        'postgres': make_component(results.get('postgres')),
        'service': service_component,
        'environment': results.get('environment')
    }

    validated = StatusResponse(**body)
    return JSONResponse(status_code=status_code, content=validated.dict())
