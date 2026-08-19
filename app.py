from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from Config.config import DevelopmentConfig
from Controller.auth_controller import auth_bp
from Controller.event_controller import event_bp
from Controller.home_controller import home_bp


db = SQLAlchemy()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
