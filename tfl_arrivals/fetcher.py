import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
from tfl_arrivals import parser, config, config_auth
from tfl_arrivals.models import Line, LineId, StopId, StopPoint, Arrival
from typing import List


def __fetch_url(url) -> str:
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1)
    s.mount('https://', HTTPAdapter(max_retries=retries))
    keys = {"app_id" : config_auth['tfl_api']['app_id'],
            "app_key" : config_auth['tfl_api']['app_key']}

    response = requests.get(url, params = keys)
    if response.status_code != 200:
        raise(f"Cannot fetch data from {url}, error {response.status_code}")
    else:
        return response.text

def __get_cache_file_name(url):
    return url.replace("https://api.tfl.gov.uk/", "").\
        replace("/", "_")

def __save_response(cache_path, url, response):
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    f = open(cache_path + __get_cache_file_name(url), "w")
    f.write(response)
    f.close()

def __load_response(cache_path, url):
    logging.debug(f"Loading url from cache ({url})")
    try:
        f = open(cache_path + __get_cache_file_name(url))
        return f.read()
    except FileNotFoundError:
        return ""

def _fetch(url) -> str:
    cache_path = "/tmp/london_arrivals_cache/"
    response = ""
    if config.getboolean("app","use_api_response_cache"):
        response = __load_response(cache_path, url)

    if response == "":
        response = __fetch_url(url)

    if config.getboolean("app","cache_api_responses"):
        __save_response(cache_path, url, response)
    return response


def _fetch_arrivals(naptan_id: LineId) -> str:
    return _fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}/Arrivals")

def _fetch_lines(mode: str) -> str:
    return _fetch(f"https://api.tfl.gov.uk/Line/Mode/{mode}")

def _fetch_line_stops(line_id: LineId) -> str:
    return _fetch(f"https://api.tfl.gov.uk/Line/{line_id}/StopPoints")

def _fetch_stops(naptan_id: StopId) -> str:
    return _fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}")

def _fetch_line_data(line_id: LineId) -> str:
    return _fetch(f"https://api.tfl.gov.uk/Line/{line_id}")


def fetch_lines(mode: str) -> List[Line]:
    return parser.parse_lines(_fetch_lines(mode))

def fetch_line_data(line_id: LineId) -> Line:
    return parser.parse_line(_fetch_line_data(line_id))

def fetch_line_stops(line_id: LineId) -> List[StopPoint]:
    return parser.parse_line_stops(_fetch_line_stops(line_id))

def fetch_stops(naptan_id: StopId) -> List[StopPoint]:
    return parser.parse_stops(_fetch_stops(naptan_id))

def fetch_arrivals(naptan_id: StopId) -> List[Arrival]:
    return parser.parse_arrivals(_fetch_arrivals(naptan_id))
