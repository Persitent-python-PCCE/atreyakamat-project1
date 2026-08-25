import os
import logging
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from Config.config import Config, DevelopmentConfig, ProductionConfig

from flask_caching import Cache

# Configure standard structured production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SeatMeUp")

db = SQLAlchemy()
jwt = JWTManager()
csrf = CSRFProtect()
cache = Cache()


def init_jwt_callbacks(jwt_manager):
    """Configure beginner-friendly JSON error responses for JWT authentication."""
    @jwt_manager.unauthorized_loader
    def custom_unauthorized_response(err_str):
        return jsonify({
            "success": False,
            "message": "Authentication required"
        }), 401

    @jwt_manager.invalid_token_loader
    def custom_invalid_token_response(err_str):
        return jsonify({
            "success": False,
            "message": "Invalid token"
        }), 401

    @jwt_manager.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired"
        }), 401


def init_db(app):
    """Create database tables if needed (used in development / testing)."""
    with app.app_context():
        db.create_all()


def create_app(config_class=None):
    """Application factory for SeatMeUp."""
    if config_class is None:
        env = os.environ.get("FLASK_ENV", os.environ.get("ENVIRONMENT", "development")).lower()
        if env == "production":
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)
    
    # Load configuration
    if isinstance(config_class, type):
        app.config.from_object(config_class())
    else:
        app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    init_jwt_callbacks(jwt)

    # Initialize CSRF Protection
    csrf.init_app(app)

    # Initialize Cache with SimpleCache (in-memory, in-process)
    app.config.setdefault("CACHE_TYPE", "SimpleCache")
    app.config.setdefault("CACHE_DEFAULT_TIMEOUT", 60)
    cache.init_app(app)

    # Apply ProxyFix for reverse proxies (Cloudflare Tunnel / Gunicorn) if enabled
    if app.config.get("USE_PROXY_FIX"):
        # x_for=1, x_proto=1, x_host=1, x_prefix=1 for trusted single-proxy reverse setups (Cloudflare Tunnel)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        logger.info("ProxyFix middleware enabled for reverse proxy / Cloudflare Tunnel.")

    # Ensure runtime directories exist safely
    runtime_dirs = [
        os.path.join(app.root_path, "uploads"),
        os.path.join(app.root_path, "static", "uploads"),
        os.path.join(app.root_path, "static", "uploads", "event_posters"),
        os.path.join(app.root_path, "static", "uploads", "user_documents"),
        os.path.join(app.root_path, "static", "generated_tickets"),
    ]
    for rdir in runtime_dirs:
        os.makedirs(rdir, exist_ok=True)

    # Initialize Swagger / OpenAPI documentation
    from Config.swagger_docs import init_swagger
    init_swagger(app)

    # Context processor to make current_user available to all Jinja2 templates
    @app.context_processor
    def inject_user():
        from Controller.auth_guards import get_current_user_info
        return dict(current_user=get_current_user_info())

    # Register blueprints (with CSRF exemptions for REST API blueprints)
    from api import register_blueprints
    register_blueprints(app, csrf=csrf)

    # Also register Web page controllers (protected by CSRF)
    from Controller.home_controller import home_bp
    from Controller.web_event_controller import web_event_bp
    from Controller.web_customer_controller import web_customer_bp
    from Controller.web_admin_controller import web_admin_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(web_event_bp)
    app.register_blueprint(web_customer_bp)
    app.register_blueprint(web_admin_bp)


    # Error handlers for web & API requests (secure, no stack traces leaked)
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "message": "CSRF validation failed"}), 400
        return render_template(
            "error.html",
            message="CSRF validation failed. Please refresh the page and try again.",
            status_code=400,
        ), 400

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "message": "Resource not found"}), 404
        return render_template("error.html", message="The page you requested was not found.", status_code=404), 404

    @app.errorhandler(403)
    def handle_403(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "message": "Access forbidden"}), 403
        return render_template("error.html", message="You do not have permission to access this resource.", status_code=403), 403

    @app.errorhandler(500)
    def handle_500(e):
        logger.error("Internal server error encountered on path: %s", request.path)
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "message": "Internal server error"}), 500
        return render_template("error.html", message="An unexpected error occurred. Please try again.", status_code=500), 500

    logger.info("SeatMeUp application initialized successfully.")
    return app


# Export application instance for WSGI servers (Gunicorn / Waitress)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
