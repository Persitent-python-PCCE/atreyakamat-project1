from .base_dao import BaseDAO


class UserDAO(BaseDAO):
    def get_by_email(self, email):
        """Fetch a user by email from the database."""
        return None

    def create(self, user):
        """Insert a new user record."""
        return user
