import os
from dotenv import load_dotenv

if not os.environ.get("RAILWAY_STATIC_URL"):
    load_dotenv(override=True)

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # FORCE SQLite only
    SQLITE_PATH = os.path.join(basedir, "instance", "portfolio.db")
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + SQLITE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(basedir, "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
