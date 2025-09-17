import logging
from app.models.communication_event import Communication_event

logger = logging.getLogger(__name__)

class SearchCommunication_event:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for communication_events.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Communication_event)
        for key, value in filters.items():
            if hasattr(Communication_event, key):
                query = query.filter(getattr(Communication_event, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
