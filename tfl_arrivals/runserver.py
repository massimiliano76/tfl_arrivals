"""
This script runs the tfl_arrivals application using a development server.
"""

from os import environ
from tfl_arrivals import app, arrival_db
from os import path


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    db_path = path.join(app.root_path, "arrivals.db")
    arrival_db.init(db_path)
    app.config.update(dict(
        DATABASE=db_path,
        DEBUG=True
        ))

    app.run(HOST, PORT)
