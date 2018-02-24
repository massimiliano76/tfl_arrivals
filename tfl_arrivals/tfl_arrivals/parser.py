from typing import List, Dict
from tfl_arrivals.arrival_data import Arrival, StopId, VehicleId, Line, StopPoint
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

def parse_lines(raw_json: str) -> List[Line]:
    lines = []
    for raw in json.loads(raw_json):
        line = Line(line_id = raw["id"],
                    name = raw["name"],
                    mode_name = raw["modeName"])
        lines.append(line)
    return lines


def _parse_stop(stop_json) -> StopPoint:    
    return StopPoint(naptan_id = stop_json["naptanId"],
                name = stop_json["commonName"],
                indicator = stop_json["indicator"] if "indicator" in stop_json else "")

def parse_line_stops(raw_json: str) -> List[StopPoint]:
    stops = []    
    for raw in json.loads(raw_json):    
        stop = _parse_stop(raw)
        stops.append(stop)
    return stops

def parse_stop(raw_json: str) -> StopPoint:
    return _parse_stop(json.loads(raw_json))
