"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, Response
from tfl_arrivals import app
from tfl_arrivals.arrival_data import Arrival, MonitoredStop, StopPoint, Line, db
from tfl_arrivals.prepopulate import populate_line_stops, populate_stop
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


@app.route('/arrivals')
def arrivals():    
    stops = db.session.query(MonitoredStop).all()
    
    arrivals_by_stop = {}
    for stop in stops:
        logging.info(f"stop.naptan_id = {stop.naptan_id}")
        name = db.session.query(StopPoint.name).filter(StopPoint.naptan_id == stop.naptan_id).scalar()
        logging.info(f"name = {name}")
        arrivals_by_stop[name] = db.session.query(Arrival).\
            filter(Arrival.naptan_id == stop.naptan_id).\
            filter(Arrival.ttl > datetime.now()).\
            order_by(Arrival.expected).\
            limit(5).all()

    return render_template("arrival_boards.html", stops=arrivals_by_stop)    



@app.route('/api/stops/<string:line_id>')
def line_stops(line_id):
    def get_all_stops_for_line():
        return db.session.query(StopPoint).filter(StopPoint.lines.any(line_id = line_id)).all()

    stops = get_all_stops_for_line()
    if len(stops) == 0:
        line = db.session.query(Line).filter(Line.line_id == line_id).one()
        populate_line_stops(line, db.session)
        stops = get_all_stops_for_line()
    
    db.session.commit()
    resp = Response("[" + ", ".join([stop.json() for stop in stops]) + "]", status=200, mimetype='application/json')
    return resp
    

@app.route('/api/add_monitored_stop/<string:new_naptan_id>', methods=["POST"])
def add_monitored_stop(new_naptan_id):    
    if db.session.query(StopPoint).filter(StopPoint.naptan_id == new_naptan_id).count() == 0:
        populate_stop(new_naptan_id)

    new_stop = MonitoredStop(naptan_id = new_naptan_id)
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
