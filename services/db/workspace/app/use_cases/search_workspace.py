import logging
from app.models.workspace import Workspace

logger = logging.getLogger(__name__)

class SearchWorkspace:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for workspaces.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Workspace)
        for key, value in filters.items():
            if hasattr(Workspace, key):
                query = query.filter(getattr(Workspace, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
