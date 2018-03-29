"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, Response
from tfl_arrivals import app, db_cache
from tfl_arrivals.arrival_data import Arrival, MonitoredStop, StopPoint, Line, db
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
    lines = db_cache.get_all_lines(db.session)
    return render_template("arrival_boards.html", title="London Arrivals", lines=lines)    

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
    

@app.route('/api/arrivals/<string:naptan_id>')
def api_arrivals(naptan_id):
    stop = db_cache.get_stop_point(db.session, naptan_id)
    arrivals = db_cache.get_arrivals(db.session, naptan_id)
    response_data = {"naptanId": naptan_id,
                     "name": stop.name,
                     "indicator": stop.indicator,
                     "arrivals": [{"towards" : arr.towards, 
                                   "expected" : str(arr.expected),
                                   "lineId": arr.line.name} for arr in arrivals]
                     }

    resp = Response(json.dumps(response_data) , status=200, mimetype='application/json')
    return resp


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
