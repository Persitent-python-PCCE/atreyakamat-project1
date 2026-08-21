# Controller/category_controller.py
#
# CategoryController — handles HTTP requests for category operations.
#
# Flow:
#     HTTP Request -> CategoryController -> CategoryService -> CategoryDAO -> Category Model -> MySQL

from flask import Blueprint, request, jsonify
from Services.category_service import CategoryService

category_bp = Blueprint("category_bp", __name__)
category_service = CategoryService()


@category_bp.post("")
def create_category():
    """Create a new category.

    Request Body (JSON):
        name (required), description (optional)
    """
    data = request.get_json(silent=True) or {}
    result = category_service.create_category(data)
    return jsonify(result), result.get("status", 200)


@category_bp.get("")
def list_categories():
    """List all categories."""
    result = category_service.get_all_categories()
    return jsonify(result), result.get("status", 200)


@category_bp.get("/<int:category_id>")
def get_category(category_id):
    """Get a single category by id."""
    result = category_service.get_category_by_id(category_id)
    return jsonify(result), result.get("status", 200)


@category_bp.put("/<int:category_id>")
def update_category(category_id):
    """Update a category."""
    data = request.get_json(silent=True) or {}
    result = category_service.update_category(category_id, data)
    return jsonify(result), result.get("status", 200)


@category_bp.delete("/<int:category_id>")
def delete_category(category_id):
    """Delete a category."""
    result = category_service.delete_category(category_id)
    return jsonify(result), result.get("status", 200)
