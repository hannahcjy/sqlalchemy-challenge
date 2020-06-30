import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

session = Session(engine)
#################################################
# Flask Routes
#################################################
# List all routes that are available
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp).all()

    prcp_list = []
    for i in range(len(results)):
        prcp_list.append(
            {'Date': results[i][0], 'Precipitation': results[i][1]})
        return jsonify(prcp_list)
    
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    """Return a list of all stations"""
    station_results = session.query(Station.station).all()

    stations = list(np.ravel(station_results))

    return jsonify(stations)

# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    """Return a JSON list of temperature observations(TOBS) for the previous year."""
    tob_results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= one_year_ago).all()
    
    return jsonify(tob_results)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")

def startDateOnly(date):
    day_temp_results = session.query(func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    return jsonify(day_temp_results)



# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start, end):
    multi_day_temp_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(multi_day_temp_results)


if __name__ == "__main__":
    app.run(debug=True)
