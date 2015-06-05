import flask, flask.views
from flask import url_for, request, session, redirect, jsonify, Response, make_response, current_app
from jinja2 import environment, FileSystemLoader
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin, BaseView, expose
from dateutil.parser import parse as parse_date
from flask import render_template, request
from functools import update_wrapper
from flask import session, redirect
from datetime import timedelta
from datetime import datetime
from functools import wraps
import threading
from threading import Timer
from multiprocessing.pool import ThreadPool
from time import sleep
import requests
import datetime
import time
import json
import uuid
import os


app = flask.Flask(__name__)
db = SQLAlchemy(app)
app.secret_key = '234234rfascasascqweqscasefsdvqwefe2323234dvsv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/local.db'
# os.environ['DATABASE_URL']


class Serializer(object):
  __public__ = None

  def to_serializable_dict(self):
    dict = {}
    for public_key in self.__public__:
      value = getattr(self, public_key)
      if value:
        dict[public_key] = value
    return dict


class SWEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Serializer):
      return obj.to_serializable_dict()
    if isinstance(obj, (datetime)):
      return obj.isoformat()
    return json.JSONEncoder.default(self, obj)


def SWJsonify(*args, **kwargs):
  return app.response_class(json.dumps(dict(*args, **kwargs), cls=SWEncoder, 
         indent=None if request.is_xhr else 2), mimetype='application/json')
        # from https://github.com/mitsuhiko/flask/blob/master/flask/helpers.py

class Vehicle(db.Model, Serializer):
    __public__ = ['id','sticker_no','plate_no','make','model']

    id = db.Column(db.Integer, primary_key=True)
    sticker_no = db.Column(db.String(10))
    plate_no = db.Column(db.String(10))
    make = db.Column(db.String(30))
    model = db.Column(db.String(30))

class Log(db.Model, Serializer):
    __public__ = ['id','sticker_no','plate_no','entry','exit']

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.String(20))
    exit_date = db.Column(db.String(20), default='--')
    sticker_no = db.Column(db.String(10))
    plate_no = db.Column(db.String(10))
    make = db.Column(db.String(30))
    model = db.Column(db.String(30))
    entry = db.Column(db.String(10))
    exit = db.Column(db.String(10), default='--')
    timestamp = db.Column(db.String(50))

class IngAdmin(sqla.ModelView):
    column_display_pk = True
admin = Admin(app)
admin.add_view(IngAdmin(Vehicle, db.session))
admin.add_view(IngAdmin(Log, db.session))


def log_entry(vehicle):
    log = Log(
        entry_date=time.strftime("%B %d, %Y"),
        sticker_no = vehicle.sticker_no,
        plate_no = vehicle.plate_no,
        make = vehicle.make,
        model = vehicle.model,
        entry = time.strftime("%H:%M %p"),
        timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        )
    db.session.add(log)
    db.session.commit()

    logs = Log.query.order_by(Log.timestamp.desc()).slice(0,100)

    return flask.render_template(
        'logs.html',
        logs=logs
        )

def log_exit(vehicle):
    a = Log.query.filter_by(sticker_no=vehicle.sticker_no).order_by(Log.timestamp.desc()).first()
    a.exit = time.strftime("%H:%M %p")
    a.exit_date = time.strftime("%m/%d/%y")
    db.session.commit()

    logs = Log.query.order_by(Log.timestamp.desc()).slice(0,100)

    return flask.render_template(
        'logs.html',
        logs=logs
        )


@app.route('/', methods=['GET', 'POST'])
def render_index():
    date = time.strftime("%B %d, %Y")
    logs = Log.query.order_by(Log.timestamp.desc()).slice(0,100)
    return flask.render_template('index.html', date=date, logs=logs)


@app.route('/authenticate', methods=['GET', 'POST'])
def vehicle_authentication():
    sticker_no = flask.request.form.get('sticker_no')
    vehicle = Vehicle.query.filter_by(sticker_no=sticker_no).first()
    date = time.strftime("%B %d, %Y")
    if vehicle:

        return flask.render_template(
            'vehicle_info.html',
            sticker_no=sticker_no,
            plate_no=vehicle.plate_no,
            make=vehicle.make,
            model=vehicle.model
            )

    return flask.render_template('unauthorized.html')


@app.route('/addlog', methods=['GET', 'POST'])
def log():
    sticker_no = flask.request.form.get('sticker_no')
    vehicle = Vehicle.query.filter_by(sticker_no=sticker_no).first()

    if vehicle:

        return log_entry(vehicle)

    return '', 204 


@app.route('/db/rebuild', methods=['GET', 'POST'])
def rebuild_database():
    db.drop_all()
    db.create_all()

    vehicle = Vehicle(
        sticker_no = '1234',
        plate_no = 'UUE-918',
        make = 'Honda',
        model = 'Civic'
        )

    vehicle1 = Vehicle(
        sticker_no = '4321',
        plate_no = 'UUE-345',
        make = 'Toyota',
        model = 'Corolla'
        )

    vehicle2 = Vehicle(
        sticker_no = '4567',
        plate_no = 'UUA-345',
        make = 'Mitsubishi',
        model = 'Lancer'
        )

    db.session.add(vehicle)
    db.session.add(vehicle1)
    db.session.add(vehicle2)
    db.session.commit()

    return SWJsonify({'Status': 'Database Rebuild Success'})


if __name__ == '__main__':
    app.debug = True
    app.run()

    # port=int(os.environ['PORT']), host='0.0.0.0'