from typing import Callable, List
from tfl_arrivals import db_uri, db_cache
from tfl_arrivals.models import Arrival, MonitoredStop
import time
from threading import Thread
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine


module_logger = logging.getLogger(__name__)

class arrivals_collector(object):
    """Scheduled the data collection, and saves data to the database"""
    def __init__(self, fetcher: Callable[[],str]):
        self.running = False
        self.logger = logging.getLogger(__name__)

    def start_collecting(self):
        self.logger.info("Start collecting")
        self.running = True
        self.collector_thread = Thread(target=self._run_loop)
        self.collector_thread.start()

    def stop_collecting(self):
        self.running = False

    def _run_loop(self):
        engine = create_engine(db_uri)
        session_factory = sessionmaker(bind=engine)
        session = scoped_session(session_factory)
        while self.running:
            start_time = datetime.utcnow()
            db_cache.refresh_recently_requested_stop_ids(session)
            end_time = datetime.utcnow()
            d = end_time - start_time
            self.logger.info(f"Checking/updating arrival db took {d.microseconds / 1000} ms")
            if d > timedelta(seconds=10):
                self.logger.warning(f"Updating arrival db is too slow")
            else:
                sleep_for = 10 - d.microseconds / (1000 * 1000)
                self.logger.info(f"Sleeping for {sleep_for} s")
                time.sleep(sleep_for)
