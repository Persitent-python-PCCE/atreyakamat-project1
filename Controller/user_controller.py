# Controller/user_controller.py
#
# UserController — handles HTTP requests for user operations.
#
# Architecture flow:
#     HTTP Request -> UserController -> UserService -> UserDAO -> User Model -> MySQL
#
# Responsibilities:
#   - receive the HTTP request
#   - read JSON body / URL parameters
#   - call the appropriate UserService method
#   - return the JSON response with the appropriate HTTP status code
#
# It does NOT:
#   - query the database directly
#   - contain SQLAlchemy logic
#   - contain password hashing or complex business logic

from flask import Blueprint, request, jsonify
from Services.user_service import UserService

user_bp = Blueprint("user_bp", __name__)
user_service = UserService()


@user_bp.post("")
def create_user():
    """Create a new user.

    Request Body (JSON):
        name (required), email (required), password_hash (required),
        role (optional, default "customer"), phone, id_document
    """
    data = request.get_json(silent=True) or {}
    result = user_service.create_user(data)
    return jsonify(result), result.get("status", 200)


@user_bp.get("")
def list_users():
    """List all users."""
    result = user_service.get_all_users()
    return jsonify(result), result.get("status", 200)


@user_bp.get("/<int:user_id>")
def get_user(user_id):
    """Get a single user by primary key id."""
    result = user_service.get_user_by_id(user_id)
    return jsonify(result), result.get("status", 200)


@user_bp.get("/email/<string:email>")
def get_user_by_email(email):
    """Get a single user by email address."""
    result = user_service.get_user_by_email(email)
    return jsonify(result), result.get("status", 200)


@user_bp.put("/<int:user_id>")
def update_user(user_id):
    """Update an existing user's details."""
    data = request.get_json(silent=True) or {}
    result = user_service.update_user(user_id, data)
    return jsonify(result), result.get("status", 200)


@user_bp.delete("/<int:user_id>")
def delete_user(user_id):
    """Delete a user by id."""
    result = user_service.delete_user(user_id)
    return jsonify(result), result.get("status", 200)
