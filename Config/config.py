import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "seatmeup-dev-secret-key-2026-very-secure")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "seatmeup-super-secret-jwt-key-2026-very-secure")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_CSRF_PROTECT = False  # Handled by Flask-WTF CSRFProtect for web forms; API uses Authorization header
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour valid CSRF tokens
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "3306"),
            database=os.environ.get("DB_NAME", "seatmeup"),
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__()
        secret = os.environ.get("SECRET_KEY")
        jwt_secret = os.environ.get("JWT_SECRET_KEY")
        if not secret or secret == "seatmeup-dev-secret-key-2026-very-secure":
            raise ValueError("Production SECRET_KEY must be securely configured in environment variables.")
        if not jwt_secret or jwt_secret == "seatmeup-super-secret-jwt-key-2026-very-secure":
            raise ValueError("Production JWT_SECRET_KEY must be securely configured in environment variables.")


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-jwt-secret-key"
    SECRET_KEY = "test-secret-key-csrf-seatmeup-2026"
