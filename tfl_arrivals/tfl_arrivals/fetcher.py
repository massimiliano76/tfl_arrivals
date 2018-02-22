import requests
import logging

def fetch(url):
    logging.info(f"Fetching url '{url}'")
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def url_fetcher(line_id: str, stop_id: str):
    return fetch(f"https://api.tfl.gov.uk/Line/{line_id}/Arrivals/{stop_id}?direction=inbound")

def lines_fetcher(mode: str):
    return fetch(f"https://api.tfl.gov.uk/Line/Mode/{mode}")

## Fetches arrival data from previously dumpes json files
#class file_fetcher:
#    def __init__(self, base_name):
#        self.base_name = base_name
#        self.count = 0

#    def __call__(self):
#        f = open(f"{self.base_name}_{self.count}.json", "r")
#        return json.loads(f.readline())



class fetcher(object):
    """description of class"""


