import os
import secrets


class Config:
    SECRET_KEY = secrets.token_urlsafe(64)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///sqlite.db")
    USERNAME = os.environ.get("IP_LOGGER_USERNAME", "iplogger")
    PASSWORD = os.environ.get("IP_LOGGER_PASSWORD", "1pl0gg3r")

    GEOLOCATION_DB_TOKEN = os.environ.get("IP_LOGGER_GEOLOCATION_DB_TOKEN")

    CELERY = dict(
        broker_url=os.environ.get("IP_LOGGER_CELERY_BROKER_URL", "redis://localhost"),
        result_backend=os.environ.get("IP_LOGGER_CELERY_RESULT_BACKEND", "db+sqlite:///tasks.sqlite"),
        task_ignore_result=True,
    )


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_sqlite.db"
    
    TESTING = True
    WTF_CSRF_ENABLED = False

    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY = dict(
        broker_url="memory://",
        result_backend="db+sqlite:///test_tasks.sqlite",
        task_ignore_result=True,
    )
