"""
This script runs the tfl_arrivals application using a development server.
"""

import logging
from os import environ
from tfl_arrivals import app, arrivals_collector, db
from tfl_arrivals.fetcher import url_fetcher
from os import path
import time


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(threadName)s	- %(module)s - %(levelname)s - %(message)s")

    fh = logging.FileHandler("arrivals.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

if __name__ == '__main__':
    logger = setup_logger()
    db.create_all()

    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    
    logger.info("Start live data collection")
    collector = arrivals_collector.arrivals_collector(url_fetcher)
    collector.start_collecting()
    
    app.config.update(dict(
        DEBUG=False
        ))

    logger.info(f"Start listening on {HOST}:{PORT}")
    app.run(HOST, PORT)
