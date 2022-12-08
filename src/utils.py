from flask import current_app
import random
import string
import json
import requests
from ua_parser import user_agent_parser


def generate_random_name() -> str:
    result = ''.join(random.choices(string.ascii_lowercase, k=5))
    return result


def raw_data_from_request(r) -> dict:
    result = {
        "user_agent": str(r.user_agent),
        "referrer_url": str(r.referrer),
        "headers": dict(r.headers),
        "access_route": " -> ".join(str(x) for x in r.access_route),
        "ip_info": get_ip_info_from_geolocationdb(r.remote_addr),
        "browser_info": user_agent_parser.Parse(str(r.user_agent)),
    }
    return result


def get_ip_info_from_geolocationdb(ip_address):
    token = current_app.config.get('GEOLOCATION_DB_TOKEN')
    if token:
        request_url = f'https://geolocation-db.com/jsonp/{token}/{ip_address}'
    else:
        request_url = f'https://geolocation-db.com/jsonp/{ip_address}'
    response = requests.get(request_url)
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result = json.loads(result)
    return result


def to_pretty_json(value):
    return json.dumps(value, indent=4)
