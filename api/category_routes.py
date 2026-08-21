# api/category_routes.py
#
# CONTROLLER for categories. The route bodies are now thin: read JSON,
# call CategoryService, jsonify the result.
#
#   POST   /api/categories
#   GET    /api/categories
#   GET    /api/categories/<id>
#   PUT    /api/categories/<id>
#   DELETE /api/categories/<id>

from flask import Blueprint, request, jsonify

from Services import CategoryService

category_bp = Blueprint("category_bp", __name__)
category_service = CategoryService()


@category_bp.post("")
def create_category():
    data = request.get_json(silent=True) or {}
    result = category_service.create_category(data)
    return jsonify(result), result.get("status", 200)


@category_bp.get("")
def list_categories():
    result = category_service.get_all_categories()
    return jsonify(result), result.get("status", 200)


@category_bp.get("/<int:category_id>")
def get_category(category_id):
    result = category_service.get_category_by_id(category_id)
    return jsonify(result), result.get("status", 200)


@category_bp.put("/<int:category_id>")
def update_category(category_id):
    data = request.get_json(silent=True) or {}
    result = category_service.update_category(category_id, data)
    return jsonify(result), result.get("status", 200)


@category_bp.delete("/<int:category_id>")
def delete_category(category_id):
    result = category_service.delete_category(category_id)
    return jsonify(result), result.get("status", 200)
