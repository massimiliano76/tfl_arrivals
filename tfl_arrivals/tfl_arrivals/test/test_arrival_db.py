import pytest
import os.path
import sqlite3
from tfl_arrivals.arrival_db import arrival_db, arrival_data, StopId, LineId
from typing import List
from datetime import datetime, timedelta

#def fetcher():
#    return ["2018-02-12T00:14:40+00:00", "2018-02-12T00:15:40+00:00", "Uxbridge", "123"]

#def cleanup():
#    files = ["creation_test.db", "add_remove_test.db"]
#    for f in files:


@pytest.fixture
def file_name():
    file_name = "unittest.db"
    try:
        os.remove(file_name)
    except OSError as e:
        pass

    yield file_name

    try:
        os.remove(file_name)
    except OSError as e:
        pass


def select_single_column(file_name: str, q: str) -> List[str]:    
    conn = sqlite3.connect(file_name)
    cur = conn.execute(q)
    values = [r[0] for r in cur.fetchall()]
    conn.close()
    return values

def test_db_creation(file_name):    
    db = arrival_db(file_name)
    assert os.path.isfile(file_name)
    tables = select_single_column(file_name, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    os.remove(file_name)
    assert tables == ["arrivals", "monitored_stops"]


def test_add_remove_monitored_stop(file_name):
    db = arrival_db(file_name)
    assert [] == db.get_monitored_stops()
    piccadilly = LineId("piccadilly")
    uxbridge = StopId("Uxbridge")
    knightsbridge = StopId("Knightsbridge")
    northfields = StopId("Northfields")

    db.add_monitored_stop(piccadilly, uxbridge);
    stops = db.get_monitored_stops()
    assert stops == [(piccadilly, uxbridge)]

    db.add_monitored_stop(piccadilly, knightsbridge)
    stops = db.get_monitored_stops()
    print("-" * 50)
    print(stops)
    assert stops == [(piccadilly, knightsbridge), (piccadilly, uxbridge)]
   

    db.add_monitored_stop(piccadilly, knightsbridge); # second add doesn't throw
    stops = db.get_monitored_stops()
    assert stops == [(piccadilly, knightsbridge), (piccadilly, uxbridge)]
    
    db.add_monitored_stop(piccadilly, northfields)
    stops = db.get_monitored_stops()
    assert stops == [(piccadilly, knightsbridge), (piccadilly, northfields), (piccadilly, uxbridge)]

    db.remove_monitored_stop(piccadilly, northfields)
    db.remove_monitored_stop(piccadilly, uxbridge)
    stops = db.get_monitored_stops()
    assert stops == [(piccadilly, knightsbridge)]

    db.remove_monitored_stop(LineId("x"), knightsbridge) # removing stop that is not watched doesn't throw
    db.remove_monitored_stop(piccadilly, StopId("X")) # removing stop that is not watched doesn't throw
    db.remove_monitored_stop(piccadilly, knightsbridge)
    stops = db.get_monitored_stops()
    assert stops == []

    db.remove_monitored_stop(piccadilly, knightsbridge)
    stops = db.get_monitored_stops()
    assert stops == []

def test_add_get_arrivals(file_name):
    db = arrival_db(file_name)
    assert [] == db.get_arrivals([])
    assert [] == db.get_arrivals([42])

    arrive_at1 = datetime(2017, 4, 12, 17, 23, 29)    
    ttl1 = arrive_at1 + timedelta(minutes = 20)

    arrive_at2 = datetime(2017, 4, 12, 17, 33, 29)    
    ttl2 = arrive_at2 + timedelta(minutes = 15)
    
    arrive_at3 = datetime(2017, 4, 13, 19, 13)    
    ttl3 = arrive_at3 + timedelta(minutes = 15)

    arr1 = arrival_data(234, 42, "Uxbridge", arrive_at1, ttl1)
    arr2 = arrival_data(236, 42, "Elephand and Castle", arrive_at2, ttl2)
    arr3 = arrival_data(24, 97, "Very-very long stop names should be cropped", arrive_at3, ttl3)
    orig_arrivals = [arr1, arr2, arr3]
    db.add_arrivals(orig_arrivals)
    db_arrivals = db.get_arrivals([42])
    assert sorted(db_arrivals) == sorted([arr1, arr2])

    db_arrivals = db.get_arrivals([42, 97])
    assert db_arrivals == orig_arrivals
