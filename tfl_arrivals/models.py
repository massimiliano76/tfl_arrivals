from datetime import datetime
from typing import Callable, NewType
from math import ceil
from functools import total_ordering
from tfl_arrivals import db
import enum

VehicleId = NewType("VehicleId", str)
StopId = NewType("VehicleId", str)

modes = ["tube", "bus"]

class CachedDataType(enum.Enum):
    stop_point = 1
    arrival = 2

class CacheTimestamp(db.Model):
    __tablename__ = "cache_timestamp"
    id = db.Column(db.Integer, primary_key = True)
    data_type = db.Column(db.Enum(CachedDataType), nullable = False)
    data_id = db.Column(db.String(30), nullable = True)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

class ArrivalRequest(db.Model):
    __tablename__ = "arrival_request"
    id = db.Column(db.Integer, primary_key = True)
    naptan_id = db.Column(db.String(15))
    request_time = db.Column(db.DateTime, default=datetime.utcnow)

def _b2s(b: bool) -> str:
    if b:
        return "true"
    else:
        return "false"

def _optstr2str(l: str) -> str:
    if l == None:
        return ""
    else:
        return l

class StopPoint(db.Model):
    __tablename__ = "stop_point"

    naptan_id = db.Column(db.String(15), primary_key = True)
    name = db.Column(db.String(80), nullable = False)
    url = db.Column(db.String(80), index = True, unique = True )
    indicator = db.Column(db.String(15)) # e.g. "Stop B", "just after"
    stop_letter = db.Column(db.String(8), nullable = True)
    latitude = db.Column(db.Float(precision=32), nullable = False)
    longitude = db.Column(db.Float(precision=32), nullable = False)
    sms_code = db.Column(db.String(5), nullable = True)
    mode_bus = db.Column(db.Boolean, unique = False, default = False)
    mode_cablecar = db.Column(db.Boolean, unique = False, default = False)
    mode_coach = db.Column(db.Boolean, unique = False, default = False)
    mode_dlr = db.Column(db.Boolean, unique = False, default = False)
    mode_nationalrail = db.Column(db.Boolean, unique = False, default = False)
    mode_overground = db.Column(db.Boolean, unique = False, default = False)
    mode_riverbus = db.Column(db.Boolean, unique = False, default = False)
    mode_tflrail = db.Column(db.Boolean, unique = False, default = False)
    mode_tram = db.Column(db.Boolean, unique = False, default = False)
    mode_tube = db.Column(db.Boolean, unique = False, default = False)
    lines_bus = db.Column(db.String(200), unique = False, nullable = True)
    lines_tube = db.Column(db.String(200), unique = False, nullable = True)

    def str(self) -> str:
        return f'{self.naptan_id}, {self.name}, {self.latitude}, {self.longitude}'

    def json(self) -> str:
        return f'{{"naptan_id": "{self.naptan_id}", ' +\
        f'"stop_letter": "{self.stop_letter}", ' +\
        f'"name": "{self.name}", ' +\
        f'"mode_bus": {_b2s(self.mode_bus)}, ' +\
        f'"mode_dlr": {_b2s(self.mode_dlr)}, ' +\
        f'"mode_overground": {_b2s(self.mode_overground)}, ' +\
        f'"mode_tram": {_b2s(self.mode_tram)}, ' +\
        f'"mode_tube": {_b2s(self.mode_tube)}, ' +\
        f'"lines_bus": "{_optstr2str(self.lines_bus)}", ' +\
        f'"lines_tube": "{_optstr2str(self.lines_tube)}"}}'

    def mode_list(self) -> str:
        all = [(self.mode_bus, "bus"), (self.mode_cablecar, "cable car"), (self.mode_coach, "coach"),
        (self.mode_dlr, "DLR"), (self.mode_nationalrail, "National Rail"), (self.mode_overground, "overground"),
        (self.mode_riverbus, "river bus"), (self.mode_tflrail, "TfL Rail"),
        (self.mode_tram, "tram"), (self.mode_tube, "tube")]
        return [p[1] for p in all if p[0]]

    def mode_list_string(self) -> str:
        modes = self.mode_list()
        s = ""
        if len(modes) > 2:
            s = ", ".join(modes[:-1]) + " and " + modes[-1]
        else:
            s = " and ".join(self.mode_list())
        return s


class MonitoredStop(db.Model):
    __tablename__ = "monitored_stop"

    naptan_id = db.Column(db.String(15), primary_key = True)

class Arrival(db.Model):
    """Represents one arrival"""
    __tablename__ = "arrival"
    arrival_id = db.Column(db.Integer, primary_key = True)
    line_name = db.Column(db.String(40))
    vehicle_id = db.Column(db.String(10), nullable = False)
    naptan_id = db.Column(db.String(15))
    towards = db.Column(db.String(40), nullable = False)
    destination_name = db.Column(db.String(80), nullable = False)
    expected = db.Column(db.DateTime, nullable = False)
    ttl = db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return f"Arrival(arrival_id={self.arrival_id}, line_name='{self.line_name}', " +\
               f"vehicle_id='{self.vehicle_id}', naptan_id='{self.naptan_id}', " +\
               f"towards='{self.towards}', destination_name='{self.destination_name}', " +\
               f"expected='{self.expected}', ttl='{self.ttl}')"

    def expected_in_minutes_str(self, now: Callable[[], datetime]=datetime.utcnow) -> int:
        delta = self.expected - now()
        if self.expected < now() or delta.seconds < 20:
            return "due"
        delta = self.expected - now()
        return ceil(delta.seconds/60)

    def expected_in_seconds(self, now: Callable[[], datetime]=datetime.utcnow) -> int:
        delta = self.expected - now()
        return delta.seconds

    def is_expired(self, now: Callable[[], datetime]=datetime.utcnow) -> bool:
        return self.ttl < now()

    def update_with(self, other):
        assert(self.arrival_id == other.arrival_id)
        assert(self.vehicle_id == other.vehicle_id)
        assert(self.naptan_id == other.naptan_id)
        self.towards = other.towards
        self.destination_name = other.destination_name
        self.expected = other.expected
        self.ttl = other.ttl

    def as_tuple(self):
        return (self.arrival_id, self.line_name, self.vehicle_id, self.naptan_id, self.towards, self.destination_name, self.expected, self.ttl)

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.as_tuple() == other.as_tuple()

    def __ne__(self, other) -> bool:
        return not self == other
