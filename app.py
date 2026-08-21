from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Controller.home_controller import *
from Config.config import DevelopmentConfig


db = SQLAlchemy()


def init_db(app):
    with app.app_context():
        db.create_all()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Register every API blueprint (added in the API layer).
    # We import `register_blueprints` inside create_app() on purpose, NOT at
    # the top of this file. The api package imports the DAO package, which
    # does `from app import db`. If we imported api at the top of this file,
    # `db` would not exist yet (circular import). By importing here, `db`
    # is already defined above by the time api/* loads.
    from api import register_blueprints
    register_blueprints(app)

    @app.route("/")
    def home():
        return index()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
