import time
import logging
import sqlalchemy

def wait_for_db(engine, timeout=60, interval=1):
    logger = logging.getLogger(__name__)
    start = time.time()
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            logger.info("Database connection established.")
            break
        except Exception as e:
            elapsed = time.time() - start
            if elapsed > timeout:
                logger.error(f"Could not connect to database after {timeout} seconds: {e}")
                raise
            logger.info(f"Waiting for database... ({int(elapsed)}s elapsed)")
            time.sleep(interval)
