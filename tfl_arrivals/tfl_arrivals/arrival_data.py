from datetime import datetime
from typing import Callable
from math import ceil

class arrival_data:
    """Represents one arrival"""
    def __init__(self, id: int, towards: str, expected: datetime, ttl: datetime, now: Callable[[], datetime] = datetime.now):
        self.now = now
        self.id = id
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