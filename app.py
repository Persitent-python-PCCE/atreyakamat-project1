from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from Config.config import DevelopmentConfig

db = SQLAlchemy()
jwt = JWTManager()


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

    # Context processor to make current_user available to all Jinja2 templates
    @app.context_processor
    def inject_user():
        from Controller.auth_guards import get_current_user_info
        return dict(current_user=get_current_user_info())

    # Register blueprints
    from api import register_blueprints
    register_blueprints(app)

    # Also register Web page controllers
    from Controller.home_controller import home_bp
    from Controller.web_event_controller import web_event_bp
    from Controller.web_customer_controller import web_customer_bp
    from Controller.web_admin_controller import web_admin_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(web_event_bp)
    app.register_blueprint(web_customer_bp)
    app.register_blueprint(web_admin_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
