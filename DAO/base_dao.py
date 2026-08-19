class BaseDAO:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection

    def fetch_all(self, query, params=None):
        """Return rows from the database layer."""
        if self.db_connection is None:
            return []
        return []

    def fetch_one(self, query, params=None):
        if self.db_connection is None:
            return None
        return None

    def execute(self, query, params=None):
        if self.db_connection is None:
            return None
        return None
