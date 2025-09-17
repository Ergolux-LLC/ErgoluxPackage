# app/infrastructure/database/postgres.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.utils.config import Config

config = Config()

DATABASE_URL = (
    f"postgresql+psycopg2://{config.get('DB_USER')}:"
    f"{config.get('DB_PASS')}@{config.get('DB_HOST')}:"
    f"{config.get('DB_PORT')}/{config.get('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)