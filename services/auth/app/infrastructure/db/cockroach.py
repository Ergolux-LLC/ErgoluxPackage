# app/infrastructure/db/cockroach.py

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Resolve project root based on the main entry point
main_module = sys.modules.get("__main__")
main_file = getattr(main_module, "__file__", None)

if main_file is None:
    raise RuntimeError("Unable to determine project root from __main__.__file__")

project_root = Path(main_file).resolve().parent
load_dotenv(dotenv_path=project_root / ".env")

# Required environment variables (must match .env exactly)
required_vars = [
    "COCKROACH_USER",
    "COCKROACH_PASSWORD",
    "COCKROACH_HOST",
    "COCKROACH_PORT",
    "COCKROACH_DB",
    "COCKROACH_SSL",
]

missing = [var for var in required_vars if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

# Get values
COCKROACH_USER = os.getenv("COCKROACH_USER")
COCKROACH_PASSWORD = os.getenv("COCKROACH_PASSWORD", "")
COCKROACH_HOST = os.getenv("COCKROACH_HOST")
COCKROACH_PORT = os.getenv("COCKROACH_PORT")
COCKROACH_DB = os.getenv("COCKROACH_DB")
COCKROACH_SSL = os.getenv("COCKROACH_SSL")

sslmode = "require" if COCKROACH_SSL == "true" else "disable"

# Connection string
DATABASE_URL = (
    f"cockroachdb://{COCKROACH_USER}:{COCKROACH_PASSWORD}@"
    f"{COCKROACH_HOST}:{COCKROACH_PORT}/{COCKROACH_DB}"
    f"?sslmode={sslmode}"
)

def get_engine():
    return create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def get_sessionmaker():
    engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
