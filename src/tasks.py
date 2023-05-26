import uuid
import logging

from flask import Flask

from sqlalchemy.orm.attributes import flag_modified
from celery import Celery, Task, shared_task

from src.models import Click, db
from src.utils import get_ip_info


logger = logging.getLogger(__name__)

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


@shared_task
def ip_info_request(click_uuid: uuid.uuid4) -> None:
    click = Click.query.filter_by(uuid=click_uuid).first()
    click.raw_data["ip_details"] = get_ip_info(str(click.ip_address))
    logger.info(f"IP info for {click.ip_address}: {click.raw_data['ip_details']}")
    db.session.commit()
    logger.info(f"IP info for {click.ip_address} saved")
