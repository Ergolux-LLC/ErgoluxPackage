import logging
from app.models.location import Location

logger = logging.getLogger(__name__)

class SearchLocation:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for locations.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Location)
        for key, value in filters.items():
            if hasattr(Location, key):
                query = query.filter(getattr(Location, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
