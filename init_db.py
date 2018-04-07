from tfl_arrivals import db
from tfl_arrivals.arrival_data import *

db.create_all()
db.session.commit()
