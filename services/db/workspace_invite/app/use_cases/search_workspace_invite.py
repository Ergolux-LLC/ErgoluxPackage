import logging
from app.models.workspace_invite import Workspace_invite

logger = logging.getLogger(__name__)

class SearchWorkspace_invite:
    def __init__(self, relational_db):
        self.relational_db = relational_db

    def execute(self, limit=20, offset=0, **filters):
        """
        Paginated search for workspace_invites.
        Returns (results, total).
        """
        query = self.relational_db.db.query(Workspace_invite)
        for key, value in filters.items():
            if hasattr(Workspace_invite, key):
                query = query.filter(getattr(Workspace_invite, key) == value)
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        return results, total
