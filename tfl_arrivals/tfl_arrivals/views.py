"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect
from tfl_arrivals import app
from tfl_arrivals.arrival_db import arrival_data, arrival_db
import json
from os import path

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

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
    db_path = path.join(app.root_path, "arrivals.db")
    db = arrival_db(db_path)
    data = json.loads(request.data)
    print(f"Processing add_monitored_stop, {data}")
    db.add_monitored_stop(data["line_id"], data["stop_id"])
    return ""

@app.route('/arrivals')
def arrivals():    
    db_path = path.join(app.root_path, "arrivals.db")
    db = arrival_db(db_path)    
    arrivals = db.get_all_arrivals()
    arrivals_by_stop = {}
    for arr in arrivals:
        if arr.stop_id in arrivals_by_stop:
            arrivals_by_stop[arr.stop_id].append(arr)
        else:
            arrivals_by_stop[arr.stop_id] = [arr]
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
