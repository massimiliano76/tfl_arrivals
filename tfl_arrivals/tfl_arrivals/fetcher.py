import requests

def url_fetcher(line_id: str, stop_id: str):
    url = f"https://api.tfl.gov.uk/Line/{line_id}/Arrivals/{stop_id}?direction=inbound" 
    print(f"Fetching url '{url}'")
    return requests.get(url).text



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


