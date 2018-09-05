from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List of all available API routes"""
    return (
        "Welcome to the Hawaiian weather API!<br/>"
        "Available Routes below:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "NOTE: For the following two calls, dates (start and end) must be in %Y-%m-%d format<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query 
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-23', Measurement.date < '2018-01-01').order_by(Measurement.date).all()
    all_results = []
    for result in results:
        result_dict = {}
        result_dict["date"] = result.date
        result_dict["prcp"] = result.prcp
        all_results.append(result_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset."""

    # Pull all stations and station names from Station
    results = session.query(Station.name).all()
    
    # Create a list to track our results to eventually turn into a JSON
    station_list = []
    
    # Loop through the query results and add the station name to the list
    for x in results:
        station_list.append(x.name)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temps():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""

    # Define the datetime one year prior to the max date in the dataset
    year_prior = dt.datetime.strptime('2016-08-23', '%Y-%m-%d')
    
    # Query for all temperature observations in the last year of the dataset
    results = session.query(Measurement.tobs).filter(Measurement.date >= year_prior).all()
    
    tobs_list = []
    for x in results:
        tobs_list.append(x.tobs)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_dt(start):
    """Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start range i.e. for all dates greater than or equal to the start date.
    If the date requested is above the maximum date, return a 404 error."""

    # Define the datetime one year prior to the max date in the dataset
    try:
        start_dttm = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "dates must be in %Y-%m-%d format"}), 404       
    
    # Query for all temperature observations from start date forward
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_dttm).all()
    
    tobs_list = []
    for x in results:
        tobs_list.append(x.tobs)
    
    if tobs_list != []:
        result_dict = {
            'TMIN': min(tobs_list),
            'TMAX': max(tobs_list),
            'TAVG': np.mean(tobs_list)
        }

        return jsonify(result_dict)
    
    # If the date is past the max date in the dataset, produce a 404 error
    return jsonify({"error": "start date is past the maximum date in the dataset"}), 404


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for dates between the start and end date inclusive.
    If the start date requested is above the maximum date, return a 404 error.
    If the end date is less than the start date, return a 404 error."""

    # Define the datetime one year prior to the max date in the dataset
    try: 
        start_dttm = dt.datetime.strptime(start, '%Y-%m-%d')
        end_dttm = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "dates must be in %Y-%m-%d format"}), 404
    
    if start_dttm > end_dttm:
        return jsonify({"error": "start date cannot be greater than end date"}), 404
    
    # Query for all temperature observations from start date forward
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_dttm).filter(Measurement.date <= end_dttm).all()
    
    tobs_list = []
    for x in results:
        tobs_list.append(x.tobs)
    
    if tobs_list != []:
        result_dict = {
            'TMIN': min(tobs_list),
            'TMAX': max(tobs_list),
            'TAVG': np.mean(tobs_list)
        }

        return jsonify(result_dict)
    
    # If the date is past the max date in the dataset, produce a 404 error
    return jsonify({"error": "chosen date is past the maximum date in the dataset"}), 404

if __name__ == "__main__":
    app.run(debug=True)
