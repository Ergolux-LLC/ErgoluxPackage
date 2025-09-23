from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
import os
import logging
from pathlib import Path

load_dotenv()

# Configure logging with file output for log aggregation
log_dir = Path("/app/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.FileHandler('/app/logs/account_setup.log'),
        logging.StreamHandler()  # Keep console output for development
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting Account Setup service with file logging enabled")

app = FastAPI()

# Import routes (skeleton)
from routes import router
app.include_router(router)

@app.get("/status")
def status():
    logger.info("Status endpoint called")
    return {"status": "account_setup ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
