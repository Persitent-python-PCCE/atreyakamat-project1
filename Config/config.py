import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_db_uri() -> str:
    """Resolve database URI from DATABASE_URL or individual DB_* variables."""
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return db_url
    user = os.environ.get("DB_USER", "root")
    password = os.environ.get("DB_PASSWORD", "")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    database = os.environ.get("DB_NAME", "seatmeup")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "seatmeup-dev-secret-key-2026-very-secure")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "seatmeup-super-secret-jwt-key-2026-very-secure")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_CSRF_PROTECT = False  # Handled by Flask-WTF CSRFProtect for web forms; API uses Authorization header
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour valid CSRF tokens
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application Domain / Base URL for links & tickets
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "")

    # Reverse Proxy / Cloudflare Tunnel Support
    USE_PROXY_FIX = os.environ.get("USE_PROXY_FIX", "false").lower() in ("true", "1", "yes")

    # Mail / Gmail SMTP Configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", os.environ.get("SMTP_HOST", "smtp.gmail.com"))
    MAIL_PORT = int(os.environ.get("MAIL_PORT", os.environ.get("SMTP_PORT", "587")))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", os.environ.get("GMAIL_ADDRESS", ""))
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", ""))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")

    # Session & Cookie Security Defaults (Relaxed for local development)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False

    # Uploads Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    UPLOAD_FOLDER = os.path.join(str(BASE_DIR), "static", "uploads")
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration with strict secret validation and secure cookie headers."""
    DEBUG = False
    TESTING = False
    USE_PROXY_FIX = os.environ.get("USE_PROXY_FIX", "true").lower() in ("true", "1", "yes")

    # Secure cookies under HTTPS (can be disabled via COOKIE_SECURE=false for local HTTP testing)
    _cookie_secure = os.environ.get("COOKIE_SECURE", "true").lower() in ("true", "1", "yes")
    SESSION_COOKIE_SECURE = _cookie_secure
    JWT_COOKIE_SECURE = _cookie_secure
    WTF_CSRF_SSL_STRICT = _cookie_secure

    def __init__(self):
        super().__init__()
        secret = os.environ.get("SECRET_KEY")
        jwt_secret = os.environ.get("JWT_SECRET_KEY")
        if not secret or secret == "seatmeup-dev-secret-key-2026-very-secure":
            raise ValueError(
                "Production SECRET_KEY must be securely configured in environment variables (.env)."
            )
        if not jwt_secret or jwt_secret == "seatmeup-super-secret-jwt-key-2026-very-secure":
            raise ValueError(
                "Production JWT_SECRET_KEY must be securely configured in environment variables (.env)."
            )


class TestingConfig(Config):
    """Isolated Testing environment configuration."""
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-jwt-secret-key"
    SECRET_KEY = "test-secret-key-csrf-seatmeup-2026"
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False
