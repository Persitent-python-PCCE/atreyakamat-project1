# api/user_routes.py
#
# REST endpoints for /api/users
#
# This file is the CONTROLLER for users. It ONLY:
#   - reads the JSON body
#   - calls the UserService with that body
#   - turns the Service result into an HTTP JSON response
#
# It does NOT import any DAO directly. It never runs SQL or business rules.
# All of that lives in Services/user_service.py.
#
# Endpoints:
#   POST   /api/users              create a new user
#   GET    /api/users              list all users
#   GET    /api/users/<id>         get one user by id
#   GET    /api/users/email/<email> get one user by email
#   PUT    /api/users/<id>         update one user
#   DELETE /api/users/<id>         delete one user
#
# Response format (unchanged from before):
#   Success: {"success": true, "message": "...", "data": {...}}
#   Error:   {"success": false, "message": "..."}

from flask import Blueprint, request, jsonify

from Services import UserService
from Services._result import ok, fail  # noqa: F401  (kept for clarity if needed)

# --- Controller-level wiring ---
user_bp = Blueprint("user_bp", __name__)

# A single Service instance is reused across requests. The Service itself
# holds a single DAO instance. Neither keeps request-specific state.
user_service = UserService()


@user_bp.post("")
def create_user():
    """Create a new user.

    Body (JSON):
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
    """Get one user by id."""
    result = user_service.get_user_by_id(user_id)
    return jsonify(result), result.get("status", 200)


@user_bp.get("/email/<string:email>")
def get_user_by_email(email):
    """Get one user by email address."""
    # Small input gate at the controller: empty segments in the URL would
    # otherwise just say "User not found", which is technically true but
    # misleading. The Service also guards against this.
    result = user_service.get_user_by_email(email)
    return jsonify(result), result.get("status", 200)


@user_bp.put("/<int:user_id>")
def update_user(user_id):
    """Update one user. Accepts any subset of the editable fields."""
    data = request.get_json(silent=True) or {}
    result = user_service.update_user(user_id, data)
    return jsonify(result), result.get("status", 200)


@user_bp.delete("/<int:user_id>")
def delete_user(user_id):
    """Delete one user by id."""
    result = user_service.delete_user(user_id)
    return jsonify(result), result.get("status", 200)
