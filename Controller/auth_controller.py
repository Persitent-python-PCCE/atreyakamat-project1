# Controller/auth_controller.py
#
# AuthController — handles authentication for REST API and Jinja2 Web routes.
#
# Endpoints:
#   API:
#     POST /api/auth/register
#     POST /api/auth/login
#     GET  /api/auth/me
#     GET  /api/auth/customer-test
#     GET  /api/auth/admin-test
#     POST /api/auth/logout
#   Web:
#     GET/POST /login
#     GET/POST /register
#     GET      /logout

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    make_response,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
)

from Services.auth_service import AuthService
from Controller.auth_guards import role_required

api_auth_bp = Blueprint("api_auth_bp", __name__)
web_auth_bp = Blueprint("web_auth_bp", __name__)
from api.schemas import RegisterRequestSchema, LoginRequestSchema, validate_payload

auth_service = AuthService()


# ==================================================================== #
# API AUTH ENDPOINTS
# ==================================================================== #

@api_auth_bp.post("/register")
def api_register():
    """Register a new customer account via API."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(RegisterRequestSchema, data)
    if err_resp:
        return err_resp
    result = auth_service.register(validated_data)
    return jsonify(result), result.get("status", 200)


@api_auth_bp.post("/login")
def api_login():
    """Log in with email & password and receive a JWT access token."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(LoginRequestSchema, data)
    if err_resp:
        return err_resp
    result = auth_service.login(validated_data["email"], validated_data["password"])
    return jsonify(result), result.get("status", 200)


@api_auth_bp.get("/me")
@jwt_required()
def api_me():
    """Get the profile of the currently authenticated user."""
    user_id = int(get_jwt_identity())
    result = auth_service.get_me(user_id)
    return jsonify(result), result.get("status", 200)


@api_auth_bp.get("/customer-test")
@jwt_required()
@role_required("customer", "admin")
def customer_test():
    """Protected endpoint accessible to authenticated customers and admins."""
    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    return jsonify({
        "success": True,
        "message": "Customer endpoint accessed successfully",
        "data": {
            "user_id": user_id,
            "role": role
        }
    }), 200


@api_auth_bp.get("/admin-test")
@jwt_required()
@role_required("admin")
def admin_test():
    """Protected endpoint accessible ONLY to admins."""
    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    return jsonify({
        "success": True,
        "message": "Admin endpoint accessed successfully",
        "data": {
            "user_id": user_id,
            "role": role
        }
    }), 200


@api_auth_bp.post("/logout")
def api_logout():
    """Log out API client."""
    response = jsonify({"success": True, "message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200


# ==================================================================== #
# WEB (JINJA2) AUTH ROUTES
# ==================================================================== #

@web_auth_bp.route("/login", methods=["GET", "POST"])
def web_login():
    """Render and process the web login form."""
    error = None
    success_msg = None
    if request.args.get("registered"):
        success_msg = "Account created successfully! Please log in."

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        result = auth_service.login(email, password)
        if result.get("success"):
            token = result["data"]["token"]
            user_role = result["data"]["user"]["role"]
            redirect_target = (
                url_for("web_admin_bp.admin_dashboard")
                if user_role == "admin"
                else url_for("web_customer_bp.customer_dashboard")
            )
            response = make_response(redirect(redirect_target))
            # Store JWT in cookie so browser requests stay authenticated
            set_access_cookies(response, token)
            return response
        else:
            error = result.get("message")
    return render_template("auth/login.html", error=error, success_msg=success_msg)


@web_auth_bp.route("/register", methods=["GET", "POST"])
def web_register():
    """Render and process the web registration form."""
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip()

        # Validate confirm_password if supplied in form
        if confirm_password and password != confirm_password:
            error = "Passwords do not match"
            return render_template("auth/register.html", error=error)

        result = auth_service.register({
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
        })
        if result.get("success"):
            # Automatically establish login session for newly registered user and redirect to dashboard
            login_result = auth_service.login(email, password)
            if login_result.get("success"):
                token = login_result["data"]["token"]
                user_role = login_result["data"]["user"]["role"]
                redirect_target = (
                    url_for("web_admin_bp.admin_dashboard")
                    if user_role == "admin"
                    else url_for("web_customer_bp.customer_dashboard")
                )
                response = make_response(redirect(redirect_target))
                set_access_cookies(response, token)
                return response
            return redirect(url_for("web_auth_bp.web_login", registered="true"))
        else:
            error = result.get("message")
            if "already registered" in (error or "").lower():
                error = "An account with this email already exists."
    return render_template("auth/register.html", error=error)


@web_auth_bp.route("/logout")
def web_logout():
    """Log out web user by clearing the JWT access cookie."""
    response = make_response(redirect(url_for("home_bp.index")))
    unset_jwt_cookies(response)
    return response
