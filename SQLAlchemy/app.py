from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
 
#########################################################################
# Home Page
#########################################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
#########################################################################
# Precipitation by Date over a Year
#########################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365) 
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_twelve_months).all()

    precip = {date: prcp for date, prcp in rain}
        
    return jsonify(precip)

#########################################################################
# Station Names
#########################################################################
@app.route("/api/v1.0/stations")
def stations():

    stations_all = session.query(Station.name, Station.station).all()
    stations = {name: station for name, station in stations_all}
    return jsonify(stations)

#########################################################################
# Temperature Observations over a Year
#########################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365) 

    lastyear = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_twelve_months).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()

    temps = {date: tobs for date, tobs in lastyear}
    return jsonify(temps)

#########################################################################
# Start Date Only
#########################################################################
@app.route("/api/v1.0/<start>")
def start(start=None):
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    tobs_only = session.query(Measurement.tobs).filter(Measurement.date.between(start, latest_date)).all()

    tobs_df = pd.DataFrame(tobs_only)

    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()

    return jsonify(tmin, tavg, tmax)

#########################################################################
# Start & End Date
#########################################################################
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    tobs_only = session.query(Measurement.tobs).filter(Measurement.date.between(start, end)).all()

    tobs_df = pd.DataFrame(tobs_only)

    tavg = tobs_df["tobs"].mean()
    tmax = tobs_df["tobs"].max()
    tmin = tobs_df["tobs"].min()

    return jsonify(tmin, tavg, tmax)

if __name__ == "__main__":
    app.run(debug=True)