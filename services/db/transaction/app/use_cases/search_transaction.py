import logging
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

class SearchTransaction:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for transactions.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Transaction)
        for key, value in filters.items():
            if hasattr(Transaction, key):
                query = query.filter(getattr(Transaction, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
