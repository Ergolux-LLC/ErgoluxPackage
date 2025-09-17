# app/dev/clear_and_populate_db.py
import os
import uuid
import logging
from sqlalchemy import create_engine, MetaData, insert
from app.common.config import Config
from app.infrastructure.db.schema.user_table import users
from app.common.utility import hash_password

# ——— Logging setup —————————————
# 1. Disable all loggers below ERROR
logging.disable(logging.ERROR)
# 2. But re-enable root logger so errors still show
logging.getLogger().setLevel(logging.ERROR)

def build_engine(config: Config):
    user = config.get("POSTGRES_USER")
    password = config.get("POSTGRES_PASSWORD")
    host = config.get("POSTGRES_HOST")
    port = config.get("POSTGRES_PORT")
    db = config.get("POSTGRES_DB")
    ssl = config.get("POSTGRES_SSL")

    sslmode = "require" if ssl.lower() == "true" else "disable"
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}?sslmode={sslmode}"

    return create_engine(url, echo=False)

def wipe_data(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    with engine.begin() as conn:
        for table in reversed(metadata.sorted_tables):
            conn.execute(table.delete())

def seed_users(engine):
    with engine.begin() as conn:
        conn.execute(
            insert(users).values(
                id=str(uuid.uuid4()),
                email="user@example.com",
                password_hash=hash_password("secretpassword"),
                email_verified=True,
                is_active=True
            )
        )

if __name__ == "__main__":
    config = Config(os.path.join(os.path.dirname(__file__), "../.env"))
    engine = build_engine(config)

    print("Wiping all table data...")
    wipe_data(engine)

    print("Seeding test user...")
    seed_users(engine)

    print("Done.")
