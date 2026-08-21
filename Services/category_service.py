# Services/category_service.py
#
# Business logic for categories.
# Same pattern as UserService: validate input, call DAO, return a result dict.

from DAO import CategoryDAO
from models.category import Category
from api.serializers import category_to_dict
from Services._result import ok, fail


class CategoryService:
    def __init__(self):
        self.category_dao = CategoryDAO()

    # ---------------- CREATE ----------------
    def create_category(self, data: dict) -> dict:
        """Create a category. Required: name. Optional: description."""
        name = data.get("name")
        if not name or (isinstance(name, str) and not name.strip()):
            return fail("Missing required field: name", 400)

        # uniqueness check (gives a cleaner 409 than letting MySQL reject it)
        if self.category_dao.get_category_by_name(name) is not None:
            return fail("Category name already exists", 409)

        category = Category(
            name=name,
            description=data.get("description"),
        )
        try:
            saved = self.category_dao.create_category(category)
        except Exception:
            return fail("Could not create category", 500)
        return ok("Category created", category_to_dict(saved), status=201)

    # ---------------- READ ----------------
    def get_category_by_id(self, category_id: int) -> dict:
        category = self.category_dao.get_category_by_id(category_id)
        if category is None:
            return fail("Category not found", 404)
        return ok("Category retrieved", category_to_dict(category))

    def get_all_categories(self) -> dict:
        cats = self.category_dao.get_all_categories()
        return ok("Categories retrieved", [category_to_dict(c) for c in cats])

    # ---------------- UPDATE ----------------
    def update_category(self, category_id: int, data: dict) -> dict:
        category = self.category_dao.get_category_by_id(category_id)
        if category is None:
            return fail("Category not found", 404)

        if "name" in data:
            name = data["name"]
            if not name or (isinstance(name, str) and not name.strip()):
                return fail("name cannot be empty", 400)
            existing = self.category_dao.get_category_by_name(name)
            if existing is not None and existing.id != category.id:
                return fail("Category name already in use", 409)
            category.name = name

        if "description" in data:
            category.description = data["description"]

        try:
            self.category_dao.update_category(category)
        except Exception:
            return fail("Could not update category", 500)
        return ok("Category updated", category_to_dict(category))

    # ---------------- DELETE ----------------
    def delete_category(self, category_id: int) -> dict:
        category = self.category_dao.get_category_by_id(category_id)
        if category is None:
            return fail("Category not found", 404)
        try:
            self.category_dao.delete_category(category)
        except Exception:
            return fail("Could not delete category", 500)
        return ok("Category deleted")
