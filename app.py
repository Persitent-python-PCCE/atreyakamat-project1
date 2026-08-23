from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from Config.config import DevelopmentConfig

db = SQLAlchemy()
jwt = JWTManager()
csrf = CSRFProtect()


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
    with app.app_context():
        db.create_all()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    init_jwt_callbacks(jwt)

    # Initialize CSRF Protection
    csrf.init_app(app)

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

    # Error handlers for web & API requests
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
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "message": "Internal server error"}), 500
        return render_template("error.html", message="An unexpected error occurred. Please try again.", status_code=500), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
