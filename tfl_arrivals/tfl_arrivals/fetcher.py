import requests
import logging

def fetch(url):
    logging.info(f"Fetching url '{url}'")
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def url_fetcher(naptan_id: str):
    #return fetch(f"https://api.tfl.gov.uk/Line/{line_id}/Arrivals/{stop_id}?direction=inbound")
    return fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}/Arrivals")

def lines_fetcher(mode: str):
    return fetch(f"https://api.tfl.gov.uk/Line/Mode/{mode}")

def line_stops_fetcher(line_id: str):
    return fetch(f"https://api.tfl.gov.uk/Line/{line_id}/StopPoints")

def stop_fetcher(naptan_id: str):
    return fetch(f"https://api.tfl.gov.uk/StopPoint/{naptan_id}")

def line_data_fetcher(line_id: str):
    return fetch(f"https://api.tfl.gov.uk/Line/{line_id}")




class fetcher(object):
    """description of class"""


