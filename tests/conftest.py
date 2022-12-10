import os
import pytest
import base64
import tempfile

from src import create_app
from src.models import URL, db

EXAMPLE_URL = "https://example.com"

@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": db_path,
        "WTF_CSRF_ENABLED": False,
    })

    yield app

    with app.app_context():
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def auth_headers(app) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(
        f"{app.config['USERNAME']}:{app.config['PASSWORD']}".encode()).decode("utf-8")}


@pytest.fixture()
def url_obj(app):
    with app.app_context():
        url_obj = URL(url_to=EXAMPLE_URL)
        db.session.add(url_obj)
        db.session.commit()

        yield url_obj

        db.session.delete(url_obj)
        db.session.commit()
