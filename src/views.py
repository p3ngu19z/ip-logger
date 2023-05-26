import logging

from flask import Blueprint, request, redirect, render_template, url_for
from crawlerdetect import CrawlerDetect

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import desc
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from src.models import Click, URL, db
from src.forms import URLCreateForm, URLEditForm
from src.utils import raw_data_from_request, get_client_ip_address_from_request

from src.tasks import ip_info_request

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__, url_prefix='/')

auth = HTTPBasicAuth()

users = {}


@main.record
def init_auth(setup_state):
    global users
    config = setup_state.app.config
    users = {
        config["USERNAME"]: generate_password_hash(config["PASSWORD"]),
    }


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@main.route('/<path:path>', methods=["GET", "POST"])
def logger_view(path):
    url_obj = db.one_or_404(db.select(URL).filter_by(path=path))

    # Load Click_UUID if exist
    click_uuid = request.args.get('c', None)
    if click_uuid:
        click = db.one_or_404(db.select(Click).filter_by(uuid=click_uuid))
    else:
        ip_address = get_client_ip_address_from_request(request)
        click = Click(ip_address=ip_address, url=url_obj,
                      raw_data=raw_data_from_request(request))
        db.session.add(click)
        db.session.commit()

        # Start background tasks
        ip_info_request.delay(click.uuid)


    # Detect Bots
    crawler_detect = CrawlerDetect(headers=dict(request.headers), user_agent=str(request.user_agent))
    if crawler_detect.isCrawler():
        click.raw_data["is_bot"] = True
        click.raw_data["bot_type"] = crawler_detect.getMatches()
        flag_modified(click, "raw_data")
        db.session.commit()
        return redirect(url_obj.url_to)

    # Redirect if user without JS
    no_js = bool(request.args.get('nj', False))
    if no_js:
        click.raw_data["js_disabled"] = no_js
        flag_modified(click, "raw_data")
        db.session.commit()
        return redirect(url_obj.url_to)

    if request.method == "POST":
        device_info = request.json
        click.raw_data["device_info"] = device_info
        flag_modified(click, "raw_data")
        db.session.commit()
        return '', 200

    if url_obj.use_js:
        return render_template("redirector.html", url=url_obj, click_uuid=click.uuid)
    else:
        return redirect(url_obj.url_to)


@main.route('/d/<url_uuid>', methods=["GET", "POST"])
@auth.login_required
def dashboard_view(url_uuid):
    page = request.args.get("page", 1, int)
    per_page = request.args.get("per_page", 10, int)
    url = db.one_or_404(db.select(URL).filter_by(uuid=url_uuid))
    form = URLEditForm(obj=url)
    clicks = Click.query.filter_by(url_uuid=url_uuid).order_by(desc(Click.datetime)).paginate(page=page,
                                                                                              per_page=per_page)
    if form.validate_on_submit():
        url.url_to = form.url_to.data
        url.path = form.path.data
        url.use_js = form.use_js.data
        db.session.commit()
    return render_template("dashboard.html", clicks=clicks, url=url, form=form)


@main.route('/c', methods=["GET", "POST"])
@auth.login_required
def create_view():
    form = URLCreateForm()
    if form.validate_on_submit():
        url_to = form.url.data
        url = URL(url_to=url_to)
        db.session.add(url)
        db.session.commit()
        return redirect(url_for('main.dashboard_view', url_uuid=url.uuid))
    else:
        return render_template("create.html", form=form)
