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

    @app.route("/")
    def home():
        return index()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
