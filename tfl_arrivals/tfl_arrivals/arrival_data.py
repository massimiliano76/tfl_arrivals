from datetime import datetime
from typing import Callable
from math import ceil
from functools import total_ordering

@total_ordering
class arrival_data:
    """Represents one arrival"""
    def __init__(self, vehicle_id: int, 
                 stop_id: int,
                 towards: str, 
                 expected: datetime, 
                 ttl: datetime, 
                 now: Callable[[], datetime] = datetime.now):
        self.now = now
        self.vehicle_id = vehicle_id
        self.stop_id = stop_id
        self.towards = towards
        self.expected = expected
        self.ttl = ttl

    def expected_in_minutes(self) -> int:
        delta = self.expected - self.now()
        return ceil(delta.seconds/60)

    def expected_in_seconds(self) -> int:
        delta = self.expected - self.now()
        return delta.seconds

    def is_expired(self) -> bool:
        return self.ttl < self.now()
    
    def __str__(self) -> str:
        return f"{self.towards[:30]:30} {self.expected_in_minutes():2}"

    def as_tuple(self):
        return (self.vehicle_id, self.stop_id, self.expected, self.ttl, self.towards)

    def __eq__(self, other) -> bool:
        return self.as_tuple() == other.as_tuple()

    def __ne__(self, other) -> bool:
        return not self == other

    def __lt__(self, other) -> bool:
        return self.as_tuple() < other.as_tuple()

    def __repr__(self):
        return str(self.as_tuple())