# Controller/auth_controller.py
#
# AuthController — handles authentication for both REST API and Jinja2 Web routes.
#
# Endpoints:
#   API:
#     POST /api/auth/register
#     POST /api/auth/login
#     GET  /api/auth/me
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
    set_access_cookies,
    unset_jwt_cookies,
)

from Services.auth_service import AuthService

api_auth_bp = Blueprint("api_auth_bp", __name__)
web_auth_bp = Blueprint("web_auth_bp", __name__)
auth_service = AuthService()


# ==================================================================== #
# API AUTH ENDPOINTS
# ==================================================================== #

@api_auth_bp.post("/register")
def api_register():
    """Register a new customer account via API."""
    data = request.get_json(silent=True) or {}
    result = auth_service.register(data)
    return jsonify(result), result.get("status", 200)


@api_auth_bp.post("/login")
def api_login():
    """Log in with email & password and receive a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    result = auth_service.login(email, password)
    return jsonify(result), result.get("status", 200)


@api_auth_bp.get("/me")
@jwt_required()
def api_me():
    """Get the profile of the currently authenticated user."""
    user_id = int(get_jwt_identity())
    result = auth_service.get_me(user_id)
    return jsonify(result), result.get("status", 200)


# ==================================================================== #
# WEB (JINJA2) AUTH ROUTES
# ==================================================================== #

@web_auth_bp.route("/login", methods=["GET", "POST"])
def web_login():
    """Render and process the web login form."""
    error = None
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
    return render_template("auth/login.html", error=error)


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

        if password != confirm_password:
            error = "Passwords do not match"
            return render_template("auth/register.html", error=error)

        result = auth_service.register({
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
        })
        if result.get("success"):
            return redirect(url_for("web_auth_bp.web_login"))
        else:
            error = result.get("message")
    return render_template("auth/register.html", error=error)


@web_auth_bp.route("/logout")
def web_logout():
    """Log out web user by clearing the JWT access cookie."""
    response = make_response(redirect(url_for("home_bp.index")))
    unset_jwt_cookies(response)
    return response
