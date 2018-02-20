from typing import List
from tfl_arrivals.arrival_data import Arrival, StopId, VehicleId
import json 
from datetime import datetime

def parse_arrivals(raw_json: str) -> List[Arrival]:
    arrivals = []
    for raw in json.loads(raw_json):
        parse_string = "%Y-%m-%dT%H:%M:%SZ" 
        
        arrival = Arrival(arrival_id = int(raw["id"]),
                          line_id = raw["lineId"],
                          vehicle_id = VehicleId(raw["vehicleId"]),
                          naptan_id = StopId(raw["naptanId"]),
                          expected = datetime.strptime(raw["expectedArrival"], parse_string),
                          ttl = datetime.strptime(raw["timeToLive"],  parse_string),
                          towards = raw["towards"]
                          )
        arrivals.append(arrival)
    return arrivals