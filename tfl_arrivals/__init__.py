"""
The flask application package.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db_path = "sqlite:///C:\\temp\\arrivals_orm2.db" # TODO remove
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
db = SQLAlchemy(app)

import tfl_arrivals.views


