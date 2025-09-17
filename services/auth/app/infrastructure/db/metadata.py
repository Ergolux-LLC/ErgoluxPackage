# app/infrastructure/db/metadata.py
from sqlalchemy import MetaData

metadata = MetaData()

# This line is required so metadata gets populated
from app.infrastructure.db.schema import user_table
