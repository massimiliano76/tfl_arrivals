from typing import Callable, List
from tfl_arrivals import arrival_data, arrival_db, parse_arrivals
import time
from threading import Thread
import itertools
from datetime import datetime

class arrivals_collector(object):
    """Scheduled the data collection, and saves data to the database"""
    def __init__(self, db_file_name: str, fetcher: Callable[[],str]):
        self.db_file_name = db_file_name
        self.fetcher = fetcher
        self.running = False
        pass

    def collect(self) -> List[arrival_data.arrival_data]:
        self.conn = arrival_db.arrival_db(self.db_file_name)
        stops = self.conn.get_monitored_stops()
        print(f"Colecting arrival info for stops: {stops}")
        return list(itertools.chain.from_iterable([parse_arrivals.parse_arrivals(self.fetcher(*stop)) for stop in stops]))

    def start_collecting(self):
        print("Start collecting")
        self.running = True
        self.collector_thread = Thread(target=self._run_loop)
        self.collector_thread.start()        

    def stop_collecting(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            print("Updating arrival db...")
            arrivals = self.collect()
            self.conn.remove_old_arrivals(datetime.now())
            self.conn.add_arrivals(arrivals)
            time.sleep(10)
