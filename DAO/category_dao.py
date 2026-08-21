# DAO/category_dao.py
#
# CategoryDAO — the Data Access Object for the `categories` table.
# A category is a simple label used to group events (e.g. Concert, Theater).
#
# This file follows the exact same pattern as user_dao.py:
#   - one class, several small methods
#   - each method does ONE database operation
#   - no business rules, no validation logic

from app import db
from models.category import Category


class CategoryDAO:
    """Database operations for the Category model."""

    def create_category(self, category: Category) -> Category:
        """Insert a new category row.

        Args:
            category: A Category() object with name already set by the Service.

        Returns:
            The same category, now with an id assigned by the database.
        """
        try:
            db.session.add(category)
            db.session.commit()
            return category
        except Exception:
            db.session.rollback()
            raise

    def get_category_by_id(self, category_id: int) -> Category | None:
        """Load one category by its primary key. Returns None if not found."""
        return db.session.get(Category, category_id)

    def get_category_by_name(self, name: str) -> Category | None:
        """Look up a category by its name. Useful for checking duplicates.

        (name is unique on the model, so .first() is enough.)
        """
        return Category.query.filter_by(name=name).first()

    def get_all_categories(self) -> list[Category]:
        """Return every category in the database as a list."""
        return Category.query.all()

    def update_category(self, category: Category) -> Category:
        """Commit any changes the Service already applied to `category`."""
        try:
            db.session.commit()
            return category
        except Exception:
            db.session.rollback()
            raise

    def delete_category(self, category: Category) -> bool:
        """Delete the given category row. Returns True on success."""
        try:
            db.session.delete(category)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
