"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, Response, send_from_directory
from tfl_arrivals import app, db_cache, arrivals_collector, db
from tfl_arrivals.models import Arrival, StopPoint, ArrivalRequest
from tfl_arrivals.fetcher import fetch_arrivals
import json
from os import path
import logging


@app.before_first_request
def start_collector():
    collector = arrivals_collector.arrivals_collector(fetch_arrivals)
    collector.start_collecting()


@app.route('/')
def arrivals():
    return render_template(
        "arrival_boards.html",
        title="Arrivals of London",
        description="Simple, real-time arrival information for London's public transport, including bus stops, DLR and tube stations",
        year=datetime.utcnow().year)


@app.route('/about')
def about():
    return render_template(
        "arrival_boards.html",
        title="Arrivals of London",
        year=datetime.utcnow().year)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/<string:naptan_id>')
def one_stop(naptan_id):
    print("naptan_id = ", naptan_id)
    stop = db_cache.get_stop_point(db.session, naptan_id)

    mode_list = stop.mode_list_string()
    print("mode_list = ", mode_list)

    return render_template(
        "arrival_boards.html",
        title=f"{stop.name}",
        description=f"{stop.name} - live {mode_list} arrival times",
        naptan_id=naptan_id,
        id_stem=f"{naptan_id}_arrivals",
        year=datetime.utcnow().year)


@app.route('/api/stop_search/<string:query>')
def api_stop_search(query):
    stops = db_cache.search_stop(db.session, query, 100)
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
                                   "destination_name": arr.destination_name,
                                   "expected" : str(arr.expected),
                                   "lineName": arr.line_name} for arr in arrivals]
                     }

    resp = Response(json.dumps(response_data), status=200, mimetype='application/json')
    return resp

@app.route('/api/stop/<string:naptan_id>')
def api_stop_data(naptan_id):
    stop = db_cache.get_stop_point(db.session, naptan_id)
    return Response(stop.json(), status=200, mimetype='application/json')


@app.route('/api/card_template')
def card_template():
    f = open(path.join(app.root_path, "templates/card.html"))
    return Response(f.readlines(), status=200, mimetype='text/html')
