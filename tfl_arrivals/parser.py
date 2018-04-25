import logging
from typing import List, Dict
from tfl_arrivals.models import Arrival, StopId, VehicleId, StopPoint
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
                          line_name = raw["lineName"],
                          vehicle_id = VehicleId(raw["vehicleId"]),
                          naptan_id = StopId(raw["naptanId"]),
                          expected = datetime.strptime(raw["expectedArrival"], parse_string),
                          ttl = datetime.strptime(raw["timeToLive"],  parse_string),
                          towards = raw["towards"],
                          destination_name = dest
                          )
        arrivals.append(arrival)
    return arrivals

def _parse_stop(stop_json) -> StopPoint:
    def get_optional(json, key):
        return json[key] if key in stop_json else ""

    modes = set(stop_json["modes"])
    return StopPoint(naptan_id = stop_json["naptanId"],
                name = stop_json["commonName"],
                indicator = get_optional(stop_json, "indicator"),
                stop_letter = get_optional(stop_json, "stopLetter"),
                latitude = float(stop_json["lat"]),
                longitude = float(stop_json["lon"]),
                sms_code = get_optional(stop_json, "smsCode"),
                mode_bus = "bus" in modes,
                mode_cablecar = "cable-car" in modes,
                mode_coach = "coach" in modes,
                mode_dlr = "dlr" in modes,
                mode_nationalrail = "national-rail" in modes,
                mode_overground = "overground" in modes,
                mode_riverbus = "river-bus" in modes,
                mode_tflrail = "tflrail" in modes,
                mode_tram = "tram" in modes,
                mode_tube = "tube" in modes
                )


monitoredTypes = ["NaptanPublicBusCoachTram", "NaptanMetroStation", "NaptanCoachBay"]

def _parse_stops(stop_json) -> List[StopPoint]:
    stops = []
    if stop_json == None:
        return stops

    if stop_json["stopType"] in monitoredTypes:
        if len(stop_json["lines"]) != 0:
            stops.append(_parse_stop(stop_json))

    for child in stop_json["children"]:
        stops += _parse_stops(child)
    return stops

def parse_stops(raw_json: str) -> List[StopPoint]:
    return _parse_stops(json.loads(raw_json))
