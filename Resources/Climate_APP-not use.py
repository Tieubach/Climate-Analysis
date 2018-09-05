import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Mea = Base.classes.measurement
Sta = Base.classes.station

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
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/< start ><br/>"
        f"/api/v1.0/< start >< end >"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query 
    results = session.query(Mea.date, Mea.prcp).filter(Mea.date > '2016-12-31', Mea.date < '2018-01-01').order_by(Mea.date).all()
    all_results = []
    for result in results:
        result_dict = {}
        result_dict["date"] = result.date
        result_dict["prcp"] = result.prcp
        all_results.append(result_dict)

    return jsonify(all_results)


@app.route("/api/v1.0/stations")
def stations():
    # Return a json list of stations from the dataset.
    # Query
    results = session.query(Sta.station, Sta.name).all()
    all_stas = []
    for result in results:
        result_dict = {}
        result_dict['station'] = result.station
        result_dict['name'] = result.name
        all_stas.append(result_dict)

    return jsonify(all_stas)


@app.route("/api/v1.0/tobs")
def tobss():
    results = session.query(Mea.date, Mea.tobs).filter(Mea.date > '2016-12-31', Mea.date < '2018-01-01').all()
    all_tobs = []
    for result in results:
        result_dict = {}
        result_dict['date'] = result.date
        result_dict['tobs'] = result.tobs
        all_tobs.append(result_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def descr(start, end=None):
    if end == None: end = session.query(Mea.date).order_by(Mea.date.desc()).first()[0]
    tobs = pd.read_sql(session.query(Mea.tobs).filter(Mea.date > start, Mea.date <= end).statement, session.bind)
    
    tobs_dict = {}
    tobs_dict["TMIN"] = tobs.describe().loc[tobs.describe().index=='min']['tobs'][0]
    tobs_dict["TAVG"] = tobs.describe().loc[tobs.describe().index=='mean']['tobs'][0]
    tobs_dict["TMAX"] = tobs.describe().loc[tobs.describe().index=='max']['tobs'][0]
    
    return jsonify(tobs_dict)

if __name__ == '__main__':
    app.run(debug=True)
print("TVAG,TMAX and TMIN are:",res_list)  