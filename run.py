import logging

from src import create_app
from src.models import db

logger = logging.getLogger(__name__)

app = create_app()

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logging.warning(f"Can't create database: {e}")
