from typing import List
from tfl_arrivals.arrival_data import arrival_data, StopId, VehicleId
import json 
from datetime import datetime

def parse_arrivals(raw_json: str) -> List[arrival_data]:
    arrivals = []
    for raw in json.loads(raw_json):
        parse_string = "%Y-%m-%dT%H:%M:%SZ" 
        vehicle_id = VehicleId(int(raw["vehicleId"]))
        stop_id = StopId(raw["naptanId"])
        expected = datetime.strptime(raw["expectedArrival"], parse_string)
        ttl = datetime.strptime(raw["timeToLive"],  parse_string)
        arrival = arrival_data(vehicle_id, stop_id, raw["towards"], expected, ttl)
        arrivals.append(arrival)
    return arrivals