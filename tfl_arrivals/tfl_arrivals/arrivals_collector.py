from typing import Callable, List
from tfl_arrivals import parser, db_path
from tfl_arrivals.arrival_data import Arrival, MonitoredStop
import time
from threading import Thread
import itertools
from datetime import datetime
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine



module_logger = logging.getLogger(__name__)

class arrivals_collector(object):
    """Scheduled the data collection, and saves data to the database"""
    def __init__(self, fetcher: Callable[[],str]):
        self.fetcher = fetcher
        self.running = False
        self.logger = logging.getLogger(__name__)

    def collect(self, session) -> List[Arrival]:
        stops = session.query(MonitoredStop).all()
        self.logger.debug(f"Colecting arrival info for stops: {stops}")
        all_arrivals = [parser.parse_arrivals(self.fetcher(stop.naptan_id)) for stop in stops]
        return list(itertools.chain.from_iterable(all_arrivals))

    def start_collecting(self):
        self.logger.info("Start collecting")
        self.running = True
        self.collector_thread = Thread(target=self._run_loop)
        self.collector_thread.start()        

    def stop_collecting(self):
        self.running = False

    def _run_loop(self):
        engine = create_engine(db_path)
        session_factory = sessionmaker(bind=engine)
        session = scoped_session(session_factory)
        while self.running:
            self.logger.info("Updating arrival db...")
            live_arrivals = self.collect(session)
            self.logger.info(f"Fetched {len(live_arrivals)} arrivals")
            ids = [arr.arrival_id for arr in live_arrivals]
            self.logger.debug(f"Fetched arrival ids: {ids}")
            for live_arrival in live_arrivals:
                db_arrival = session.query(Arrival).filter(Arrival.arrival_id == live_arrival.arrival_id).first()
                if db_arrival is None:
                    db_arrival = live_arrival
                    session.add(db_arrival)
                else:
                    db_arrival.update_with(live_arrival)
            
            session.commit()
            time.sleep(10)
