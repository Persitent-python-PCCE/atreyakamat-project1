# tests/unit/test_category_service.py
#
# Pure unit tests for CategoryService with mocked CategoryDAO.
# WHY: Categories structure the event marketplace. Validates name checks and retrieval.

import pytest
from unittest.mock import MagicMock
from Services.category_service import CategoryService
from models.category import Category


@pytest.mark.unit
class TestCategoryService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.cat_service = CategoryService()
        self.mock_dao = MagicMock()
        self.cat_service.category_dao = self.mock_dao

    def test_get_all_categories(self):
        """WHY: Listing all categories returns full catalog."""
        self.mock_dao.get_all_categories.return_value = [
            Category(id=1, name="Music"),
            Category(id=2, name="Sports"),
        ]
        res = self.cat_service.get_all_categories()
        assert res["success"] is True
        assert len(res["data"]) == 2

    def test_create_category_missing_name(self):
        """WHY: Category creation requires non-empty name."""
        res = self.cat_service.create_category({"description": "No name given"})
        assert res["success"] is False
        assert res["status"] == 400

    def test_create_category_duplicate_name(self):
        """WHY: Category name must be unique."""
        self.mock_dao.get_category_by_name.return_value = Category(id=1, name="Music")
        res = self.cat_service.create_category({"name": "Music"})
        assert res["success"] is False
        assert res["status"] == 409
