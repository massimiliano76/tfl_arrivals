import sqlite3
from typing import List, Tuple, Callable
import os
from tfl_arrivals.arrival_data import arrival_data, StopId, LineId, VehicleId
from datetime import datetime
from dateutil import parser
import logging

module_logger = logging.getLogger(__name__)

class arrival_db:
    def __init__(self, db_path: str):
        self.logger = logging.getLogger(__name__)        
        self.db_path = db_path
        if not os.path.isfile(db_path):
            self.logger.info(f"Creating database at {db_path}")
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
            line_id string NOT NULL,
            stop_id string NOT NULL,
            PRIMARY KEY(line_id, stop_id)
            )""")

    def add_monitored_stop(self, line_id: LineId, stop_id: StopId) -> None:
        try:
            self._db_query(f"INSERT INTO monitored_stops (line_id, stop_id) VALUES ('{line_id}', '{stop_id}')")
        except sqlite3.IntegrityError:
            pass

    def remove_monitored_stop(self, line_id: LineId, stop_id: StopId) -> None:
        self._db_query(f"DELETE FROM monitored_stops WHERE stop_id = '{stop_id}' AND line_id = '{line_id}'")

    def get_monitored_stops(self) -> List[Tuple[LineId, StopId]]:
        cur = self._db_query("SELECT line_id, stop_id FROM monitored_stops ORDER BY line_id, stop_id")
        stops = []
        for r in cur.fetchall():
            stops.append((r[0], r[1]))
        #stops = [(r[0], r[1]) for r in cur.fetchall()]
        return stops

    def remove_old_arrivals(self, ts: datetime):
        q = f"DELETE FROM arrivals WHERE ttl < '{ts}'"
        curr = self._db_query(q)

    def remove_arrival(self, vehicle_id: VehicleId, stop_id: StopId):
        q = f"DELETE FROM arrivals WHERE vehicle_id == {vehicle_id} AND stop_id = '{stop_id}'"
        curr = self._db_query(q)
        
    def add_arrivals(self, arrivals: List[arrival_data]) -> None:
        for arr in arrivals:
            self.remove_arrival(arr.vehicle_id, arr.stop_id)

        q = "INSERT INTO arrivals (vehicle_id, expected, ttl, towards, stop_id) VALUES (?, ?, ?, ?, ?)"
        tuple_args = [(a.vehicle_id, a.expected, a.ttl, a.towards, a.stop_id) for a in arrivals]
        self._db_query(q, tuple_args)

    def get_arrivals(self, stop_ids: List[StopId]) -> List[arrival_data]:
        str_ids = ", ".join([str(id) for id in stop_ids])
        q = f"""SELECT vehicle_id, stop_id, towards, expected, ttl 
            FROM arrivals 
            WHERE stop_id IN ({str_ids}) 
            ORDER BY ttl DESC
            LIMIT 3
            """
        curr = self._db_query(q)
        return [arrival_data(r[0], r[1], r[2], parser.parse(r[3]), parser.parse(r[4])) for r in curr.fetchall()]



    def get_all_arrivals(self) -> List[arrival_data]:
        stop_ids = self.get_monitored_stops()
        str_ids = ", ".join([str(id[1]) for id in stop_ids])
        q = f"""SELECT vehicle_id, stop_id, towards, expected, ttl 
            FROM arrivals 
            WHERE stop_id IN ('{str_ids}')
            ORDER BY ttl DESC   
            LIMIT 3
            """
        curr = self._db_query(q)
        return [arrival_data(r[0], r[1], r[2], parser.parse(r[3]), parser.parse(r[4])) for r in curr.fetchall()]
        
    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _db_query(self, query: str, args = None) -> sqlite3.Cursor:
        conn = self._get_conn()
        cur = None
        try:
            if args == None:
                self.logger.debug(f"query='{query}'")
                cur = conn.execute(query)
            else:
                self.logger.debug(f"query='{query}', args={args}")
                cur = conn.executemany(query, args)
        except Exception as e:
            self.logger.error("Unable to execute query: " + str(e))

        conn.commit()
        return cur
