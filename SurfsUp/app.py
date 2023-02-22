from flask import Flask, json, jsonify
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()

Base.prepare(engine, reflect=True)

# Saving data to table

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print()
    return (
        f'Welcome to the Honolulu climate analysis page<br><br>'
        f'These are the available routes:<br>'
        f'/api/v1.0/precipitation<br>'
        f'/api/v1.0/stations<br>'
        f'/api/v1.0/&lt;start_date&gt;<br>'
        f'/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(bind=engine)
    
    # Get the latest date and the year before that
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    previous_year = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date.between(previous_year, latest_date)).order_by(measurement.date).all()
    
    session.close()
    
    # Saving results to dictionary
    result_dict = dict(results)
    print(f"Precipitation Results - {result_dict}")
    return jsonify(result_dict) 

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(bind=engine)
    
    # Fetching the list of stations and their corresponding names
    results = session.query(station.station, station.name).all()

    session.close()
    
    # Saving results to dictionary
    station_list = dict(results)
    return jsonify(station_list)

@app.route('/api/v1.0/tobs/')
def tobs():
    
    session = Session(bind=engine)
    
    # Getting the station with the highest count
    counter = session.query(measurement.station).order_by(func.count(measurement.station).desc()).first()

    # We can get the start and end dates using the calculated data above
    latest_date = session.query(measurement.date).filter(measurement.station == counter[0]).order_by(measurement.date.desc()).first().date
    previous_year = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.tobs).filter(measurement.date.between(previous_year, latest_date)).order_by(measurement.date).all()
    
    session.close()

    # Saving results to dictionary
    tobs = dict(results)
    return jsonify(tobs)

@app.route('/api/v1.0/<start_date>/')
def start(start_date):

    session = Session(bind=engine)

    agg_select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*agg_select).filter(measurement.date >= start_date).all()
    
    session.close()

    # Saving results to list
    temp_list = [round(i, 1) for i in results[0]]

    return jsonify(temp_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def start_end(start_date, end_date):

    session = Session(bind=engine)
    
    agg_select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*agg_select).filter(measurement.date.between(start_date, end_date)).all()
    
    session.close()
    
    # Saving results to list
    temp_list = [round(i, 1) for i in results[0]]

    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)