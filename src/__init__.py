import logging
from flask import Flask

logger = logging.getLogger(__name__)

def create_app(config='src.config.Config'):
    app = Flask(__name__)
    
    app.config.from_object(config)

    from src.models import db
    db.init_app(app)

    from src.views import main
    app.register_blueprint(main)

    from src.tasks import celery_init_app
    app.config.from_prefixed_env()
    celery_init_app(app)

    from src.utils import to_pretty_json
    app.jinja_env.filters['tojson_pretty'] = to_pretty_json

    return app
