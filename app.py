"""
This script runs the tfl_arrivals application using a development server.
"""

from os import environ
from tfl_arrivals import app
from os import path
import time
import sys
from tfl_arrivals.models import *

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5000'))
    except ValueError:
        PORT = 5000

    app.config.update(dict(
        DEBUG=True
        ))

    app.run(HOST, PORT)
