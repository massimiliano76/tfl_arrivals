import logging
from typing import List, Dict
from tfl_arrivals.models import Arrival, StopId, VehicleId, Line, StopPoint
import json
from datetime import datetime

module_logger = logging.getLogger(__name__)


def parse_arrivals(raw_json: str) -> List[Arrival]:
    arrivals = []
    for raw in json.loads(raw_json):
        parse_string = "%Y-%m-%dT%H:%M:%SZ"
        if "destinationName" in raw:
            dest = raw["destinationName"]
        else:
            raw["towards"]
        arrival = Arrival(arrival_id = int(raw["id"]),
                          line_id = raw["lineId"],
                          vehicle_id = VehicleId(raw["vehicleId"]),
                          naptan_id = StopId(raw["naptanId"]),
                          expected = datetime.strptime(raw["expectedArrival"], parse_string),
                          ttl = datetime.strptime(raw["timeToLive"],  parse_string),
                          towards = raw["towards"],
                          destination_name = dest
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

def parse_line(raw_json: str) -> Line:
    raw = json.loads(raw_json)[0]
    return Line(line_id = raw["id"],
                name = raw["name"],
                mode_name = raw["modeName"])

def _parse_stop(stop_json) -> StopPoint:
    return StopPoint(naptan_id = stop_json["naptanId"],
                name = stop_json["commonName"],
                indicator = stop_json["indicator"] if "indicator" in stop_json else "")


monitoredTypes = ["NaptanPublicBusCoachTram", "NaptanMetroStation", "NaptanCoachBay"]

def _parse_stops(stop_json) -> List[StopPoint]:
    stops = []
    if stop_json == None:
        return stops

    if stop_json["stopType"] in monitoredTypes:
        stops.append(_parse_stop(stop_json))

    for child in stop_json["children"]:
        stops += _parse_stops(child)
    return stops

def parse_line_stops(raw_json: str) -> List[StopPoint]:
    stops = []
    for raw in json.loads(raw_json):
        stop = _parse_stop(raw)
        stops.append(stop)
    return stops

def parse_stops(raw_json: str) -> List[StopPoint]:
    return _parse_stops(json.loads(raw_json))
