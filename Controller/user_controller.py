# Controller/user_controller.py
#
# UserController — handles HTTP requests for user operations.
#
# Flow:
#     HTTP Request -> UserController -> UserService -> UserDAO -> User Model -> MySQL

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Services.user_service import UserService
from Controller.auth_guards import role_required

from api.schemas import UserCreateRequestSchema, UserUpdateRequestSchema, validate_payload

user_bp = Blueprint("user_bp", __name__)
user_service = UserService()


@user_bp.post("")
@jwt_required()
@role_required("admin")
def create_user():
    """Create a new user (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(UserCreateRequestSchema, data)
    if err_resp:
        return err_resp
    result = user_service.create_user(validated_data)
    return jsonify(result), result.get("status", 200)


@user_bp.get("")
@jwt_required()
@role_required("admin")
def list_users():
    """List all users (Admin only)."""
    result = user_service.get_all_users()
    return jsonify(result), result.get("status", 200)


@user_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """Get a single user by id (Admin or account owner)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")
    if current_role != "admin" and current_user_id != user_id:
        return jsonify({"success": False, "message": "You do not have permission to access this resource"}), 403

    result = user_service.get_user_by_id(user_id)
    return jsonify(result), result.get("status", 200)


@user_bp.get("/email/<string:email>")
@jwt_required()
@role_required("admin")
def get_user_by_email(email):
    """Get a single user by email address (Admin only)."""
    result = user_service.get_user_by_email(email)
    return jsonify(result), result.get("status", 200)


@user_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id):
    """Update an existing user's details (Admin or account owner)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")
    if current_role != "admin" and current_user_id != user_id:
        return jsonify({"success": False, "message": "You do not have permission to access this resource"}), 403

    data = request.get_json(silent=True) or {}
    # Non-admins cannot promote themselves to admin
    if current_role != "admin" and "role" in data:
        data.pop("role")

    validated_data, err_resp = validate_payload(UserUpdateRequestSchema, data, partial=True)
    if err_resp:
        return err_resp

    result = user_service.update_user(user_id, validated_data)
    return jsonify(result), result.get("status", 200)


@user_bp.delete("/<int:user_id>")
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    """Delete a user by id (Admin only)."""
    result = user_service.delete_user(user_id)
    return jsonify(result), result.get("status", 200)
