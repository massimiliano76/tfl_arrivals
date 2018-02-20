"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for
from tfl_arrivals import app
from tfl_arrivals.arrival_data import Arrival, MonitoredStop, db
import json
from os import path
import logging

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return redirect(url_for("arrivals"))


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/add_monitored_stop', methods=["POST"])
def add_monitored_stop():    
    data = json.loads(request.data)
    logging.info(f"Processing add_monitored_stop, {data}")
    new_stop = MonitoredStop(naptan_id = data["naptan_id"], line_id = data["line_id"])
    db.session.add(new_stop)
    db.session.commit()    
    return ""

@app.route('/arrivals')
def arrivals():    
    arrivals = db.session.query(Arrival).limit(3).all()
    arrivals_by_stop = {}
    for arr in arrivals:
        if arr.naptan_id in arrivals_by_stop:
            arrivals_by_stop[arr.naptan_id].append(arr)
        else:
            arrivals_by_stop[arr.naptan_id] = [arr]
    return render_template("arrival_boards.html", stops=arrivals_by_stop)    


#@app.route('/arrivals')
#def home():
#    """Renders the next three arrivals at all monitored stations"""
#    db = arrival_db('arrivals.db')
#    #db.get_arrivals()
#    return render_template(
#        'arrival_boards.html',
#        title='Arrivals',
#        year=datetime.now().year,
#    )


#@app.route('/about')
#def about():
#    """Renders the about page."""
#    return render_template(
#        'contact.html',
#        title='About',
#        year=datetime.now().year,
#        message='Your application description page.'
#    )
