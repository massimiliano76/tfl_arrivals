"""
This script runs the tfl_arrivals application using a development server.
"""

import logging
from os import environ
from tfl_arrivals import app, arrivals_collector, db
from tfl_arrivals.fetcher import fetch_arrivals
from os import path
import time
import sys


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


def init_db():    
    db.create_all()

if __name__ == '__main__':
    logger = setup_logger()

    if len(sys.argv) == 2 and sys.argv[1] == "init":
        init_db()
        exit()

    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    
    logger.info("Start live data collection")
    collector = arrivals_collector.arrivals_collector(fetch_arrivals)
    #collector.start_collecting()
    
    app.config.update(dict(
        DEBUG=True
        ))

    logger.info(f"Start listening on {HOST}:{PORT}")
    app.run(HOST, PORT)
