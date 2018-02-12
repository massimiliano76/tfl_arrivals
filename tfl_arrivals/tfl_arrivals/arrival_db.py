import sqlite3
import threading
from typing import List, Tuple
import time
import os

__db_path = ""

def init(db_path: str) -> None:
    __db_path = db_path
    os.remove(__db_path)
    db = sqlite3.connect(__db_path)
    _create_db(db)
    threading.Thread(target=update_arrivals).start()


def get_arrivals(stop_id: str) -> List[Tuple[str, int]]:
    return []

def add_monitored_stop(stop_id: int) -> None:
    db = _get_db()
    q = "INSERT INTO monitored_stops (stop_id) VALUES (?)"
    db.execute(q, [stop_id])
    db.commit()

def update_arrivals():
    db = _get_db()
    while True:
        q = "INSERT INTO arrivals (date, ttl, towards, stop_id) VALUES (?, ?, ?, ?)"
        _db_query(_db, q, ["2018-02-12T00:14:40+00:00", "2018-02-12T00:15:40+00:00", "Uxbridge", "123"])
        print("1 line inserted")
        time.sleep(10)

def _get_db():
    return sqlite3.connect(__db_path)
    




def _db_query(db, query: str, args = None) -> None:
    try:
        if args == None:
            db.execute(query)
        else:
            db.execute(query, args)
        print("DB Success: " + query)
    except Exception as e:
        print("Unable to create databse table: " + e)
    db.commit()

def _create_db(db) -> None:
    _db_query(db, """CREATE TABLE arrivals(
        date TEXT NOT NULL,
        ttl TEXT NOT NULL,
        towards TEXT NOT NULL,
        stop_id INT NOT NULL
        )""")


    _db_query(db, """CREATE TABLE monitored_stops(
        stop_id INT NOT NULL
        )""")

