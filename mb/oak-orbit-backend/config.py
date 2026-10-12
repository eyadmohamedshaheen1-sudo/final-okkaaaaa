import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB max request body (image uploads as base64)
    SEND_FILE_MAX_AGE_DEFAULT = 0         # always serve fresh JS/CSS while developing
