import os
import secrets


class Config:
    SECRET_KEY = secrets.token_urlsafe(64)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///sqlite.db")
    USERNAME = os.environ.get("USERNAME", "iplogger")
    PASSWORD = os.environ.get("PASSWORD", "1pl0gg3r")

    GEOLOCATION_DB_TOKEN = os.environ.get("GEOLOCATION_DB_TOKEN")
