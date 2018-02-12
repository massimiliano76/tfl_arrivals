import pytest
from datetime import datetime, timedelta
from tfl_arrivals.arrival_data import arrival_data

def test_to_string(capsys):
    arrive_at = datetime(2017, 4, 12, 17, 23, 29)
    t_minus_one = datetime(2017, 4, 12, 17, 23, 25, 0)
    ttl = datetime(2017, 4, 12, 17, 23, 40, 0)
    dummy_now = lambda : t_minus_one
    arr = arrival_data(42, "Uxbridge", arrive_at, ttl, now=dummy_now)
    assert str(arr) == "Uxbridge                        1"

    arrive_at = datetime(2017, 4, 12, 17, 24, 25)
    ttl = datetime(2017, 4, 12, 17, 10, 40, 0)
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    arr = arrival_data(42, "Elephand and Castle", arrive_at, ttl, now=dummy_now)
    assert str(arr) == "Elephand and Castle            15"

    arrive_at = datetime(2017, 4, 12, 17, 24, 25)
    ttl = datetime(2017, 4, 12, 17, 10, 40, 0)
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    arr = arrival_data(42, "Very-very long stop names should be cropped", arrive_at, ttl, now=dummy_now)
    assert str(arr) == "Very-very long stop names shou 15"

def test_expected_in_seconds_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 29 == arr.expected_in_seconds()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 59)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 59 == arr.expected_in_seconds()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 69)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 69 == arr.expected_in_seconds()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 5, seconds = 23)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 323 == arr.expected_in_seconds()


def test_expected_in_seconds_real():    
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = arrival_data(0, "X", expected, expected)
    assert 29 == arr.expected_in_seconds()

    delta = timedelta(seconds = 99)
    expected = datetime.now() + delta
    arr = arrival_data(0, "X", expected, expected)
    assert 99 == arr.expected_in_seconds()


def test_expected_in_minutes_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 0)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 1 == arr.expected_in_minutes()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 59)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 1 == arr.expected_in_minutes()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 69)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 2 == arr.expected_in_minutes()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 5, seconds = 23)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 6 == arr.expected_in_minutes()
    
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(minutes = 3)
    expected = dummy_now() + delta
    arr = arrival_data(0, "X", expected, dummy_now(), dummy_now)
    assert 3 == arr.expected_in_minutes()


def test_expected_in_minutes_real():    
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = arrival_data(0, "X", expected, expected)
    assert 1 == arr.expected_in_minutes()

    delta = timedelta(seconds = 99)
    expected = datetime.now() + delta
    arr = arrival_data(0, "X", expected, expected)
    assert 2 == arr.expected_in_minutes()

def test_is_expired_mocked():
    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    ttl = dummy_now() + delta
    arr = arrival_data(0, "X", expected, ttl, dummy_now)
    assert not arr.is_expired()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(milliseconds = 1)
    expected = dummy_now() + delta
    ttl = dummy_now() + delta
    arr = arrival_data(0, "X", expected, ttl, dummy_now)
    assert not arr.is_expired()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(seconds = 29)
    expected = dummy_now() + delta
    ttl = dummy_now() - delta
    arr = arrival_data(0, "X", expected, ttl, dummy_now)
    assert arr.is_expired()

    dummy_now = lambda : datetime(2017, 4, 12, 17, 10, 11, 23)
    delta = timedelta(milliseconds = 1)
    expected = dummy_now() + delta
    ttl = dummy_now() - delta
    arr = arrival_data(0, "X", expected, ttl, dummy_now)
    assert arr.is_expired()

def test_is_expired_real():
    delta = timedelta(seconds = 29)
    expected = datetime.now() + delta
    arr = arrival_data(0, "X", expected, expected)
    assert not arr.is_expired()

    delta = timedelta(seconds = 29)
    expected = datetime.now() - delta
    arr = arrival_data(0, "X", expected, expected)
    assert arr.is_expired()

    delta = timedelta(milliseconds = 2)
    expected = datetime.now() - delta
    arr = arrival_data(0, "X", expected, expected)
    assert arr.is_expired()
    
    delta = timedelta(minutes= 20)
    expected = datetime.now() - delta
    arr = arrival_data(0, "X", expected, expected)
    assert arr.is_expired()


if __name__ == "__main__":
    pytest.main()
