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

@app.route('/robots.txt')
def robots():
    return send_from_directory(path.join(app.root_path, 'static'),
        'robots.txt', mimetype='text/plain')

@app.route('/<string:stop_id>')
def one_stop(stop_id):
    stop = db_cache.get_stop_point_by_url(db.session, stop_id.lower())
    if stop == None:
        stop = db_cache.get_stop_point(db.session, stop_id)

    if stop == None:
        return redirect(url_for("arrivals"))

    arrivals = db_cache.get_arrivals(db.session, stop.naptan_id)
    mode_list = stop.mode_list_string()

    title = stop.name
    if len(stop.stop_letter) > 0 and "->" not in stop.stop_letter:
        title = f"{stop.name} ({stop.stop_letter})"
    return render_template(
        "arrival_boards.html",
        title=f"{title} - live {mode_list} times",
        description=f"The simplest real-time public transport arrival info you can find for {stop.name}, London. Select the stops you're interested in add to your list, and see only what you want to see.",
        naptan_id=stop.naptan_id,
        server_stop_name = stop.name,
        server_stop_indicator = stop.stop_letter,
        arrivals = arrivals,
        id_stem=f"{stop.naptan_id}_arrivals",
        year=datetime.utcnow().year)


@app.route('/api/stop_search/<string:query>')
def api_stop_search(query):
    stops = db_cache.search_stop(db.session, query, 100)
    if stops == None:
        json = ""
    else:
        json = "[" + ", ".join([stop.json() for stop in stops]) + "]"
        
    resp = Response(json, status=200, mimetype='application/json')
    return resp

@app.route('/api/arrivals/<string:naptan_id>')
def api_arrivals(naptan_id):
    stop = db_cache.get_stop_point(db.session, naptan_id)
    logging.info(f"Returning arrival info for {stop.naptan_id}, {stop.name} {stop.stop_letter}")
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

    # naptan_id and id_stem will be replaced on client side when a new card
    # is created, so replace them with the original placeholders here
    resp = render_template("card.html",
        naptan_id = "{{ naptan_id }}",
        id_stem = "{{ id_stem }}",
        server_stop_name = "",
        server_stop_indicator = "F",
        use_loader = True,
        arrivals = []
    )
    return Response(resp, status=200, mimetype='text/html')
