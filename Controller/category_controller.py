# Controller/category_controller.py
#
# CategoryController — handles HTTP requests for category operations.
#
# Flow:
#     HTTP Request -> CategoryController -> CategoryService -> CategoryDAO -> Category Model -> MySQL

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from Services.category_service import CategoryService
from Controller.auth_guards import role_required

from api.schemas import CategoryCreateRequestSchema, CategoryUpdateRequestSchema, validate_payload

category_bp = Blueprint("category_bp", __name__)
category_service = CategoryService()


@category_bp.post("")
@jwt_required()
@role_required("admin")
def create_category():
    """Create a new category (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(CategoryCreateRequestSchema, data)
    if err_resp:
        return err_resp
    result = category_service.create_category(validated_data)
    return jsonify(result), result.get("status", 200)


@category_bp.get("")
def list_categories():
    """List all categories (Public)."""
    result = category_service.get_all_categories()
    return jsonify(result), result.get("status", 200)


@category_bp.get("/<int:category_id>")
def get_category(category_id):
    """Get a single category by id (Public)."""
    result = category_service.get_category_by_id(category_id)
    return jsonify(result), result.get("status", 200)


@category_bp.put("/<int:category_id>")
@jwt_required()
@role_required("admin")
def update_category(category_id):
    """Update a category (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(CategoryUpdateRequestSchema, data, partial=True)
    if err_resp:
        return err_resp
    result = category_service.update_category(category_id, validated_data)
    return jsonify(result), result.get("status", 200)


@category_bp.delete("/<int:category_id>")
@jwt_required()
@role_required("admin")
def delete_category(category_id):
    """Delete a category (Admin only)."""
    result = category_service.delete_category(category_id)
    return jsonify(result), result.get("status", 200)
