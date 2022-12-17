from flask_wtf import FlaskForm
from wtforms import URLField, StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms_alchemy import Unique, model_form_factory

from src.models import URL, db

ModelForm = model_form_factory(FlaskForm)


class URLCreateForm(FlaskForm):
    url = URLField(validators=[DataRequired()])


class URLEditForm(ModelForm):
    url_to = URLField(validators=[DataRequired()])
    path = StringField(validators=[Unique(URL.path, get_session=db.session)])
    use_js = BooleanField()
