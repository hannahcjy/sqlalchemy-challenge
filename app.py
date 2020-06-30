import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

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
    """List all available api."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


#--------------------------------------------------
# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()
    
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    query_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).\
        order_by(Measurement.date).all()

    query_list = []
    for i in query_data:
        query_dict ={}
        query_dict["Date"] = i[0]
        query_dict["precipitation"] = i[1]
        query_list.append(query_dict)

    return jsonify(query_list)

#---------------------------------------------------- 
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.station, Station.name).all()

    station_list = []
    for i in stations:
        station_dict = {}
        station_dict['station'] = i[0]
        station_dict['name'] = i[1]
        station_list.append(station_dict)

    
    return jsonify(station_list)
#---------------------------------------------------------
# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
    # most_active_station  =  USC00519281

    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    """Return a JSON list of temperature observations(TOBS) for the previous year."""
    tob_data = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date >= last_year).\
        filter(Measurement.station =='USC00519281').\
        order_by(Measurement.date).all()

    query_list = []
    for i in tob_data:
        query_dict = {}
        query_dict["Date"] = i[0]
        query_dict["Temperature"] = i[1]
        query_list.append(query_dict)


    return jsonify(query_list)
#----------------------------------------
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_only(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
 
    start_only = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    query_list = []
    for i in start_only:
        query_dict = {}
        query_dict["Query Date"] = start
        query_dict["Max Temp"] = i[0]
        query_dict["Ave Temp"] = i[1]
        query_dict["Min Temp"] = i[2]
        query_list.append(query_dict)


    return jsonify(query_list)

#-------------------------------------------
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    
    start_and_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    query_list = []
    for i in start_and_end:
        query_dict = {}
        query_dict['Start Date'] = start
        query_dict['End Date'] = end
        query_dict["Max Temp"] = i[0]
        query_dict["Ave Temp"] = i[1]
        query_dict["Min Temp"] = i[2]
        query_list.append(query_dict)


    return jsonify(query_list)



if __name__ == "__main__":
    app.run(debug=True)
