from flask import current_app
import flask
import random
import string
import json
import requests
import socket

from ipwhois import IPWhois
from ua_parser import user_agent_parser


def generate_random_name() -> str:
    result = ''.join(random.choices(string.ascii_lowercase, k=5))
    return result


def get_client_ip_address_from_request(request: flask.Request) -> str:
    """
    :param request: flask request object
    :return: IP address of client
    """
    return str(request.access_route[0])

def raw_data_from_request(r) -> dict:
    result = {
        "request": {
            "user_agent": str(r.user_agent),
            "referrer_url": str(r.referrer),
            "access_route": ", ".join(str(x) for x in r.access_route),
            "headers": dict(r.headers),
        },
        "user_agent_details": parse_data_from_user_agent(str(r.user_agent)),
    }
    return result


def parse_data_from_user_agent(user_agent: str) -> dict:
    """
    {
        "string": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0",
        "user_agent": {
            "family": "Firefox",
            "major": "107",
            "minor": "0",
            "patch": null
        },
        "os": {
            "family": "Mac OS X",
            "major": "10",
            "minor": "15",
            "patch": null,
            "patch_minor": null
        },
        "device": {
            "family": "Mac",
            "brand": "Apple",
            "model": "Mac"
        }
    }
    """
    return user_agent_parser.Parse(user_agent)


def get_ip_info(ip_address: str):
    from src.models import Click
    click_with_some_ip = Click.query.filter_by(ip_address=ip_address).first()

    if ip_details := click_with_some_ip.raw_data.get("ip_details"):
        return ip_details
    else:
        return get_ip_info_from_geolocationdb(ip_address)


def get_ip_info_from_geolocationdb(ip_address: str):
    """
    :param ip_address:
    :return:
    {
        "latitude":"UA",
        "country_name":"Ukraine",
        "city":"Kyiv",
        "postal":"01001",
        "latitude":50.450001,
        "longitude":30.523333,
        "IPv4":"127.0.0.1",
        "state":"Kyiv"
    }
    """
    token = current_app.config.get('GEOLOCATION_DB_TOKEN')
    if token:
        request_url = f'https://geolocation-db.com/jsonp/{token}/{ip_address}'
    else:
        request_url = f'https://geolocation-db.com/jsonp/{ip_address}'
    try:
        response = requests.get(request_url)
    except Exception as e:
        return dict(error=str(e))
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result = json.loads(result)

    ip_info = dict(
        hostname=get_hostname_from_ip(ip_address),
        org=get_provider_from_ip(ip_address),
        region=result.get("state"),
        city=result.get("city"),
        longitude=result.get("longitude"),
        latitude=result.get("latitude"),
        country_code=result.get("country_code"),
        country_name=result.get("country_name"),
    )

    return ip_info


def get_provider_from_ip(ip_address: str) -> str:
    try:
        return next(iter(IPWhois(ip_address).lookup_rdap(depth=1).get("network", {}).get("remarks", {})), {}).get(
            "description", "")
    except Exception as e:
        return f"Error: {e}"


def get_hostname_from_ip(ip_address: str) -> str:
    try:
        return next(iter(socket.gethostbyaddr(ip_address)), "")
    except Exception as e:
        return f"Error: {e}"


def to_pretty_json(value):
    return json.dumps(value, indent=4)
