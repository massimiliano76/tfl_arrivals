"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, Response
from tfl_arrivals import app, db_cache
from tfl_arrivals.arrival_data import Arrival, MonitoredStop, StopPoint, Line, db
from tfl_arrivals.prepopulate import populate_stop
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
        year=datetime.utcnow().year,
        message='Your contact page.'
    )


@app.route('/arrivals')
def arrivals():    
    stops = db.session.query(MonitoredStop).all() ###
    
    arrivals_by_stop = {}
    for stop in stops:
        logging.info(f"stop.naptan_id = {stop.naptan_id}")
        name = db_cache.get_stop_point(db.session, stop.naptan_id).name
        arrivals_by_stop[name] = db_cache.get_arrivals(db.session, stop.naptan_id)

    return render_template("arrival_boards.html", title="Arrivals", stops=arrivals_by_stop)    

@app.route('/add_stop')
def add_stop():
    """Renders the Add stop page."""
    lines = db_cache.get_all_lines(db.session)
    return render_template(
        'add_stop.html',
        title='Add Stop',
        year=datetime.utcnow().year,
        message='Your contact page.',
        lines=lines
    )

@app.route('/api/stops/<string:line_id>')
def api_line_stops(line_id):
    stops = db_cache.get_stops_of_line(db.session, line_id)
    resp = Response("[" + ", ".join([stop.json() for stop in stops]) + "]", status=200, mimetype='application/json')
    return resp
    

@app.route('/api/add_monitored_stop/<string:new_naptan_id>', methods=["POST"])
def api_add_monitored_stop(new_naptan_id):    
    new_stop = MonitoredStop(naptan_id = new_naptan_id)
    ###
    db.session.add(new_stop)
    db.session.commit()    
    return ""

#@app.route('/arrivals')
#def home():
#    """Renders the next three arrivals at all monitored stations"""
#    db = arrival_db('arrivals.db')
#    #db.get_arrivals()
#    return render_template(
#        'arrival_boards.html',
#        title='Arrivals',
#        year=datetime.utcnow().year,
#    )


#@app.route('/about')
#def about():
#    """Renders the about page."""
#    return render_template(
#        'contact.html',
#        title='About',
#        year=datetime.utcnow().year,
#        message='Your application description page.'
#    )
