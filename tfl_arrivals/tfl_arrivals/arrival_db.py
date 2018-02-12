import sqlite3
import threading
from typing import List, Tuple, Callable
import time
import os
from tfl_arrivals.arrival_data import arrival_data
from datetime import datetime
from dateutil import parser

class arrival_db:
    def __init__(self, db_path: str): #, arrival_fetcher: Callable[[List[int]], List[arrival_data]]):
        self.db_path = db_path
#        self.updating = False
#        self.arrival_fetcher = arrival_fetcher
        if not os.path.isfile(db_path):
            self.create_db_tables()


    def create_db_tables(self) -> None:
        self._db_query("""CREATE TABLE arrivals(
            vehicle_id INT NOT NULL,
            expected TEXT NOT NULL,
            ttl TEXT NOT NULL,
            towards TEXT NOT NULL,
            stop_id INT NOT NULL
            )""")

        self._db_query("""CREATE TABLE monitored_stops(
            stop_id INT NOT NULL UNIQUE
            )""")

    #def start_updating(self) -> None:
    #    self.updating = True
    #    threading.Thread(target=self.update_arrivals).start()

    #def stop_updating(self) -> None:
    #    self.updating = False        


    def add_monitored_stop(self, stop_id: int) -> None:
        try:
            self._db_query(f"INSERT INTO monitored_stops (stop_id) VALUES ({stop_id})")
        except sqlite3.IntegrityError:
            pass

    def remove_monitored_stop(self, stop_id: int) -> None:
        self._db_query(f"DELETE FROM monitored_stops WHERE stop_id = ({stop_id})")

    def get_monitored_stops(self) -> List[int]:
        cur = self._db_query("SELECT stop_id FROM monitored_stops ORDER BY stop_id")
        stops = [r[0] for r in cur.fetchall()]
        return stops
        
    def add_arrivals(self, arrivals: List[arrival_data]) -> None:
        q = "INSERT INTO arrivals (vehicle_id, expected, ttl, towards, stop_id) VALUES (?, ?, ?, ?, ?)"
        tuple_args = [(a.vehicle_id, a.expected, a.ttl, a.towards, a.stop_id) for a in arrivals]
        self._db_query(q, tuple_args)

    def get_arrivals(self, stop_ids: List[int]) -> List[arrival_data]:
        str_ids = ", ".join([str(id) for id in stop_ids])
        q = f"SELECT vehicle_id, stop_id, towards, expected, ttl FROM arrivals WHERE stop_id IN ({str_ids})"
        curr = self._db_query(q)
        return [arrival_data(r[0], r[1], r[2], parser.parse(r[3]), parser.parse(r[4])) for r in curr.fetchall()]

    #def update_arrivals(self):
    #    while self.updating:
    #        stops = get_monitored_stops()
    #        new_arrivals = self.arrival_fetcher.fetch(stops)
    #        self.add_arrivals(new_arrivals)
    #        time.sleep(10)
        
    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _db_query(self, query: str, args = None) -> sqlite3.Cursor:
        conn = self._get_conn()
        cur = None
        try:
            if args == None:
                print(f"query='{query}'")
                cur = conn.execute(query)
            else:
                print(f"query='{query}', args={args}")
                cur = conn.executemany(query, args)
        except Exception as e:
            print("Unable to ecxecute query: " + str(e))

        conn.commit()
        return cur
