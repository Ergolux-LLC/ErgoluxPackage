import logging
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)

class SearchConversation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for conversations.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Conversation)
        for key, value in filters.items():
            if hasattr(Conversation, key):
                query = query.filter(getattr(Conversation, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
