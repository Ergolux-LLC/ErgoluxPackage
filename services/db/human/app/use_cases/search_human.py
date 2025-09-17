import logging
from app.models.human import Human

logger = logging.getLogger(__name__)

class SearchHuman:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for humans.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Human)
        for key, value in filters.items():
            if hasattr(Human, key):
                query = query.filter(getattr(Human, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
