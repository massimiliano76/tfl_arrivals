"""
The flask application package.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config.from_pyfile("tfl_arrivals.cfg")
db_path = app.config["SQLALCHEMY_DATABASE_URI"]
db = SQLAlchemy(app)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(threadName)s	- %(module)s - %(levelname)s - %(message)s")

fh = logging.FileHandler("arrivals.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

import tfl_arrivals.views
