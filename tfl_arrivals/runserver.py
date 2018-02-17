"""
This script runs the tfl_arrivals application using a development server.
"""

from os import environ
from tfl_arrivals import app, arrival_db, arrivals_collector
from tfl_arrivals.fetcher import url_fetcher
from os import path
import time

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    db_path = path.join(app.root_path, "arrivals.db")
    db = arrival_db.arrival_db(db_path)
    time.sleep(1)
    collector = arrivals_collector.arrivals_collector(db_path, url_fetcher)
    collector.start_collecting()
    print("Started")
    app.config.update(dict(
        DATABASE=db_path,
        DEBUG=True
        ))

    app.run(HOST, PORT)
