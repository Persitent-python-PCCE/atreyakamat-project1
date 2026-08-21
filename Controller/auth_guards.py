# Controller/auth_guards.py
#
# Authentication & Role-Based Access Control (RBAC) helpers.
#
# These simple decorators check:
#   1. Is the JWT valid?
#   2. Does the authenticated user have the required role ('admin' or 'customer')?

from functools import wraps
from flask import jsonify, request, redirect, url_for, render_template
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity


def role_required(*allowed_roles):
    """Decorator to ensure the authenticated user has one of the allowed roles.

    Returns HTTP 403 JSON error if the role is insufficient.

    Example:
        @user_bp.post("")
        @jwt_required()
        @role_required("admin")
        def create_user(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT in header or cookie
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "You do not have permission to access this resource"
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user_info():
    """Helper to get current authenticated user identity and claims from JWT.
    Returns (user_id, role, name, email) or (None, None, None, None) if not logged in.
    """
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            claims = get_jwt()
            return {
                "id": int(identity),
                "role": claims.get("role"),
                "name": claims.get("name"),
                "email": claims.get("email"),
            }
    except Exception:
        pass
    return None
