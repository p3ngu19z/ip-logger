import dataclasses

from flask import current_app
from dataclasses import dataclass
from typing import Optional
import random
import string
import json
import requests
import socket

from ipwhois import IPWhois
from ua_parser import user_agent_parser


@dataclass
class IPInfo:
    hostname: str
    org: str
    country_code: str
    country_name: str
    region: str
    city: str
    latitude: float
    longitude: float
    timezone: Optional[str] = str()


def generate_random_name() -> str:
    result = ''.join(random.choices(string.ascii_lowercase, k=5))
    return result


def get_client_ip_address_from_request(r) -> str:
    return str(r.access_route[0])


def raw_data_from_request(r) -> dict:
    result = {
        "user_agent": str(r.user_agent),
        "referrer_url": str(r.referrer),
        "headers": dict(r.headers),
        "access_route": ", ".join(str(x) for x in r.access_route),
        "ip_info": get_ip_info(get_client_ip_address_from_request(r)),
        "browser_info": user_agent_parser.Parse(str(r.user_agent)),
    }
    return result


def get_ip_info(ip_address):
    from src.models import Click
    click_with_some_ip = Click.query.filter_by(ip_address=ip_address).first()

    if click_with_some_ip:
        return click_with_some_ip.raw_data["ip_info"]
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
    response = requests.get(request_url)
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result = json.loads(result)

    ip_info = IPInfo(
        hostname=get_hostname_from_ip(ip_address),
        org=get_provider_from_ip(ip_address),
        region=result.get("state"),
        city=result.get("city"),
        longitude=result.get("longitude"),
        latitude=result.get("latitude"),
        country_code=result.get("country_code"),
        country_name=result.get("country_name"),
    )

    return dataclasses.asdict(ip_info)


def get_provider_from_ip(ip_address: str) -> str:
    try:
        return next(iter(IPWhois(ip_address).lookup_rdap(depth=1).get("network", {}).get("remarks", {})), {}).get(
            "description", "")
    except Exception as e:
        return f"Error: {e}"


def get_hostname_from_ip(ip_address: str) -> str:
    return next(iter(socket.gethostbyaddr(ip_address)), "")


def get_from_ip_info(ip_address: str) -> dict:
    """
    :return:
     {
        "ip": "127.0.0.1",
        "hostname": "1.0.0.127.ua.net",
        "city": "Kyiv",
        "region": "Kyiv City",
        "country": "UA",
        "loc": "50.4547,30.5238",
        "org": "AS UKRAINE",
        "postal": "01001",
        "timezone": "Europe/Kyiv",
        "readme": "https://ipinfo.io/missingauth"
    }
    """
    pass


def to_pretty_json(value):
    return json.dumps(value, indent=4)
