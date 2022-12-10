from flask import Flask


def create_app():
    app = Flask(__name__)

    from src.config import Config
    app.config.from_object(Config())

    from src.models import db
    db.init_app(app)

    from src.views import main
    app.register_blueprint(main)

    from src.utils import to_pretty_json
    app.jinja_env.filters['tojson_pretty'] = to_pretty_json

    with app.app_context():
        db.create_all()

    return app
