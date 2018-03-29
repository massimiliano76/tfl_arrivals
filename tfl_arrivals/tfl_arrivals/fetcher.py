import requests
import logging
from tfl_arrivals import parser
from tfl_arrivals.arrival_data import Line, LineId, StopId, StopPoint
from typing import List

def _fetch(url):
    logging.info(f"Fetching url '{url}'")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def _fetch_arrivals(naptan_id: LineId):
    return _fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}/Arrivals")

def _fetch_lines(mode: str):
    return _fetch(f"https://api.tfl.gov.uk/Line/Mode/{mode}")

def _fetch_line_stops(line_id: LineId):
    return _fetch(f"https://api.tfl.gov.uk/Line/{line_id}/StopPoints")

def _fetch_stops(naptan_id: StopId):
    return _fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}")

def _fetch_line_data(line_id: LineId):
    return _fetch(f"https://api.tfl.gov.uk/Line/{line_id}")


def fetch_lines(mode: str) -> List[Line]:
    return parser.parse_lines(_fetch_lines(mode))

def fetch_line_data(line_id: LineId) -> Line:
    return parser.parse_line(_fetch_line_data(line_id))

def fetch_line_stops(line_id: LineId) -> List[StopPoint]:
    return parser.parse_line_stops(_fetch_line_stops(line_id))

def fetch_stop(naptan_id: StopId):
    return parser.parse_stop(_fetch_stops(naptan_id))

def fetch_arrivals(naptan_id: StopId):
    return parser.parse_arrivals(_fetch_arrivals(naptan_id))

class fetcher(object):
    """description of class"""


