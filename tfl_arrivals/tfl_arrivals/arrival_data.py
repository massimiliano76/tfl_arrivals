from datetime import datetime
from typing import Callable, NewType
from math import ceil
from functools import total_ordering
from tfl_arrivals import db
import enum

VehicleId = NewType("VehicleId", str)
StopId = NewType("VehicleId", str)
LineId = NewType("LineId", str)

modes = ["tube", "bus"]

class CachedDataType(enum.Enum):
    line_list = 1
    stop_point = 2
    arrival = 3
    line_stops = 4
    line_data = 5


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


line_stops = db.Table("line_stops", db.metadata,
                   db.Column("line_id", db.String(30), db.ForeignKey("line.line_id")),
                   db.Column("stop_point_id", db.String(15), db.ForeignKey("stop_point.naptan_id")))

class Line(db.Model):
    __tablename__ = "line"

    line_id = db.Column(db.String(30), primary_key = True)
    name = db.Column(db.String(40), nullable = False)
    mode_name = db.Column(db.String(10), nullable = False)
    stops = db.relationship("StopPoint", secondary=line_stops, back_populates="lines")

class StopPoint(db.Model):
    __tablename__ = "stop_point"

    naptan_id = db.Column(db.String(15), primary_key = True)
    name = db.Column(db.String(40), nullable = False)
    indicator = db.Column(db.String(10)) # e.g. "Stop B"
    lines = db.relationship("Line", secondary=line_stops, back_populates="stops")

    def json(self) -> str:
        return f'{{"naptan_id": "{self.naptan_id}", "indicator": "{self.indicator}", "name": "{self.name}"}}'
    
class MonitoredStop(db.Model):
    __tablename__ = "monitored_stop"

    naptan_id = db.Column(db.String(15), primary_key = True)

class Arrival(db.Model):
    """Represents one arrival"""
    __tablename__ = "arrival"

    arrival_id = db.Column(db.Integer, primary_key = True)
    line_id = db.Column(db.String, db.ForeignKey("line.line_id"))
    vehicle_id = db.Column(db.String(10), nullable = False)
    naptan_id = db.Column(db.String(15), db.ForeignKey("monitored_stop.naptan_id"))    
    towards = db.Column(db.String(40), nullable = False)
    expected = db.Column(db.DateTime, nullable = False)
    ttl = db.Column(db.DateTime, nullable = False)
    stop = db.relationship(MonitoredStop)
    line = db.relationship("Line", uselist = False)

    def __repr__(self):
        return f"Arrival(arrival_id={self.arrival_id}, line_id='{self.line_id}', " +\
               f"vehicle_id='{self.vehicle_id}', naptan_id='{self.naptan_id}', " +\
               f"towards='{self.towards}', expected='{self.expected}', ttl='{self.ttl}')"
    
    def expected_in_minutes(self, now: Callable[[], datetime]=datetime.utcnow) -> int:
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
        self.expected = other.expected
        self.ttl = other.ttl

    def as_tuple(self):
        return (self.arrival_id, self.line_id, self.vehicle_id, self.naptan_id, self.towards, self.expected, self.ttl)

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.as_tuple() == other.as_tuple()

    def __ne__(self, other) -> bool:
        return not self == other

def arrival_display_line(arrival: Arrival, now: Callable[[], datetime]=datetime.utcnow):
    return f"{arrival.towards[:30]:30} {arrival.expected_in_minutes(now):2}"

