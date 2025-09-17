import logging
from app.models.workspace_member import Workspace_member

logger = logging.getLogger(__name__)

class SearchWorkspace_member:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for workspace_members.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Workspace_member)
        for key, value in filters.items():
            if hasattr(Workspace_member, key):
                query = query.filter(getattr(Workspace_member, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
