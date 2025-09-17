import os
import logging
import importlib

from app.interfaces.relationaldb.postgres_adapter import PostGresAdapter
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)

def seed_conversation(adapter: PostGresAdapter):
    if os.getenv("ENV", "").lower() != "dev":
        return

    session = adapter.db
    try:
        if session.query(Conversation).first():
            return  # already seeded

        module_path = f"app.dev.seed_data.conversation"
        func_name = f"get_conversation_seed_data"

        try:
            seed_module = importlib.import_module(module_path)
            get_records = getattr(seed_module, func_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"No seed function found for 'conversation': {e}")
            return

        records = get_records()
        session.add_all(records)
        session.commit()
        logger.info("Development seed data inserted for 'conversation'")
    except Exception as e:
        session.rollback()
        logger.warning(f"Failed to seed dev data for 'conversation': {e}")
    finally:
        session.close()
