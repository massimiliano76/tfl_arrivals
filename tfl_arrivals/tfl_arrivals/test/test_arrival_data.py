import pytest
from datetime import datetime, timedelta
from tfl_arrivals.arrival_data import Arrival, arrival_display_line

def test_construction():
    now = datetime.now()
    expected = now + timedelta(minutes = 2, seconds = 59)
    ttl = now + timedelta(minutes = 15)
    arr = Arrival(vehicle_id=234, naptan_id="940GZZLUKNB", towards="Acton Town", expected = expected, ttl = ttl)
    assert arr.vehicle_id == 234
    assert arr.naptan_id == "940GZZLUKNB"
    assert arr.towards == "Acton Town"
    assert arr.expected == expected
    assert arr.ttl == ttl

def test_to_string():
    arrive_at = datetime(2017, 4, 12, 17, 23, 29)
    t_minus_one = datetime(2017, 4, 12, 17, 23, 25, 0)
    ttl = datetime(2017, 4, 12, 17, 23, 40, 0)
    dummy_now = lambda : t_minus_one
    arr = Arrival(vehicle_id=234, naptan_id="940GZZLUKNB", towards="Uxbridge", expected = arrive_at, ttl = ttl)
    assert arrival_display_line(arr, dummy_now) == "Uxbridge                        1"

    arrive_at = datetime(2017, 4, 12, 17, 24, 25)
    ttl = datetime(2017, 4, 12, 17, 10, 40, 0)
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    arr = Arrival(vehicle_id=234, naptan_id="940GZZLUKNB", towards="Elephand and Castle", expected = arrive_at, ttl = ttl)
    assert arrival_display_line(arr, dummy_now) == "Elephand and Castle            15"

    arrive_at = datetime(2017, 4, 12, 17, 24, 25)
    ttl = datetime(2017, 4, 12, 17, 10, 40, 0)
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    arr = Arrival(vehicle_id=234, naptan_id="940GZZLUKNB", towards="Very-very long stop names should be cropped", expected = arrive_at, ttl = ttl)
    assert arrival_display_line(arr, dummy_now) == "Very-very long stop names shou 15"

def test_expected_in_seconds_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="940GZZLUKNB", towards="Y", expected=expected, ttl=dummy_now())
    assert 29 == arr.expected_in_seconds(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 59)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="X", towards="Y", expected=expected, ttl=dummy_now())
    assert 59 == arr.expected_in_seconds(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 69)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="X", towards="Y", expected=expected, ttl=dummy_now())
    assert 69 == arr.expected_in_seconds(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 5, seconds = 23)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="X", towards="Y", expected=expected, ttl=dummy_now())
    assert 323 == arr.expected_in_seconds(dummy_now)


def test_expected_in_seconds_real():    
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert 29 == arr.expected_in_seconds()

    delta = timedelta(seconds = 99)
    expected = datetime.now() + delta
    arr = Arrival(vehicle_id=243, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert 99 == arr.expected_in_seconds()


def test_expected_in_minutes_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 0)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=dummy_now())
    assert 1 == arr.expected_in_minutes(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 59)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=dummy_now())
    assert 1 == arr.expected_in_minutes(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 69)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=dummy_now())
    assert 2 == arr.expected_in_minutes(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 5, seconds = 23)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=dummy_now())
    assert 6 == arr.expected_in_minutes(dummy_now)
    
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 3)
    expected = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=dummy_now())
    assert 3 == arr.expected_in_minutes(dummy_now)


def test_expected_in_minutes_real():    
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert 1 == arr.expected_in_minutes()

    delta = timedelta(seconds = 99)
    expected = datetime.now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert 2 == arr.expected_in_minutes()

def test_is_expired_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    ttl = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=ttl)
    assert not arr.is_expired(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(milliseconds = 1)
    expected = dummy_now() + delta
    ttl = dummy_now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=ttl)
    assert not arr.is_expired(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    ttl = dummy_now() - delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=ttl)
    assert arr.is_expired(dummy_now)

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(milliseconds = 1)
    expected = dummy_now() + delta
    ttl = dummy_now() - delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=ttl)
    assert arr.is_expired(dummy_now)

def test_is_expired_real():
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert not arr.is_expired()

    delta = timedelta(seconds = 29)
    expected = datetime.now() - delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert arr.is_expired()

    delta = timedelta(milliseconds = 2)
    expected = datetime.now() - delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert arr.is_expired()
    
    delta = timedelta(minutes= 20)
    expected = datetime.now() - delta
    arr = Arrival(vehicle_id=234, naptan_id="Y", towards="X", expected=expected, ttl=expected)
    assert arr.is_expired()

    
