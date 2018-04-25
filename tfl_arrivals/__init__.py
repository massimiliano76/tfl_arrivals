"""
The flask application package.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import configparser
import os

def get_db_uri(app, auth):
    dba = auth["database"]
    uri = app["app"]["database"].replace("{user}", dba["user"]).\
        replace("{password}", dba["password"]).\
        replace("{host}", dba["host"]).\
        replace("{db}", dba["name"])
    return uri

app = Flask(__name__)

inst_path = app.instance_path

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(threadName)s	- %(module)s - %(levelname)s - %(message)s")

fh = logging.FileHandler(inst_path + "/arrivals.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

logger.error("inst_path = "+ inst_path)

config = configparser.ConfigParser()
config.read(inst_path + "/app.cfg")
config["app"]["cache_api_responses"] = "False"
config["app"]["use_api_response_cache"] = "False"

config_auth = configparser.ConfigParser()
config_auth.read(inst_path + "/auth.cfg")

db_uri = get_db_uri(config, config_auth)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db = SQLAlchemy(app)

import tfl_arrivals.views
