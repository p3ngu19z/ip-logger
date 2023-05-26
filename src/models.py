import uuid
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_utils import URLType, IPAddressType, UUIDType

from src.utils import generate_random_name

db = SQLAlchemy()


class URL(db.Model):
    uuid = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url_to = db.Column(URLType)
    path = db.Column(db.String(), unique=True, default=generate_random_name)
    use_js = db.Column(db.Boolean(), default=False)


class Click(db.Model):
    uuid = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    ip_address = db.Column(IPAddressType)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    url_uuid = db.Column(UUIDType(), db.ForeignKey("url.uuid"))
    url = db.relationship("URL")
    raw_data = db.Column(MutableDict.as_mutable(JSON), default=dict())
