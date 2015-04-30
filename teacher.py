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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# os.environ['DATABASE_URL']
API_KEY = 'ecc67d28db284a2fb351d58fe18965f9'
SMS_URL = 'https://post.chikka.com/smsapi/request'
CLIENT_ID = 'ef8cf56d44f93b6ee6165a0caa3fe0d1ebeee9b20546998931907edbb266eb72'
SECRET_KEY = 'c4c461cc5aa5f9f89b701bc016a73e9981713be1bf7bb057c875dbfacff86e1d'
SHORT_CODE = '29290420420'


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

class Student(db.Model, Serializer):
    __public__ = ['id','name','level','section','msisdn']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    level = db.Column(db.String(20), default='None')
    section = db.Column(db.String(30), default='None')
    msisdn = db.Column(db.String(12))

class Teacher(db.Model, Serializer):
    __public__ = ['id','name','msisdn']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    msisdn = db.Column(db.String(12))


def check_msisdn(msisdn):
    if Teacher.query.filter_by(msisdn=msisdn).one():
        return 'teacher'
    elif Student.query.filter_by(msisdn=msisdn).one():
        return 'student'
    else:
        return 'Not Found'

def process_message(message_type, msisdn, shortcode, request_id, message, timestamp):
    if check_msisdn(msisdn) == 'teacher':
        send_this = 'teacher\'s message:' + message.split(' ', 1)[0]
        reply(msisdn, send_this, request_id)

    elif check_msisdn(msisdn) == 'student':
        print 'student\'s message:' + message

    else:
        return False

    return True

def reply(msisdn, send_this, request_id):
    sent = False
    while not sent:
        try:
            r = requests.post(
                request_url,
                reply_message_options(msisdn, send_this, request_id)
                # timeout=(int(CONNECT_TIMEOUT))           
            )
            sent =True
            print r.text #update log database (put 'sent' to status)

        except requests.exceptions.ConnectionError as e:
            sleep(5)
            print "Too slow Mojo!"
            pass

def reply_message_options(msisdn, send_this, request_id):
    message_options = {
            'message_type': 'REPLY',
            'message': message,
            'client_id': CLIENT_ID,
            'mobile_number': msisdn,
            'secret_key': SECRET_KEY,
            'shortcode': SHORT_CODE,
            'request_id': request_id,
            'message_id': uuid.uuid4().hex,
            'request_cost': 'FREE'
        }
    return message_options


@app.route('/sms/receive', methods=['GET', 'POST'])
def receive_sms():
    message_type = flask.request.form.get('message_type')
    mobile_number = flask.request.form.get('mobile_number')
    shortcode = flask.request.form.get('shortcode')
    request_id = flask.request.form.get('request_id')
    message = flask.request.form.get('message')
    timestamp = flask.request.form.get('timestamp')

    if process_message(message_type, mobile_number, shortcode, request_id, message, timestamp):
        return SWJsonify({'Status': 'Accepted'})

    return SWJsonify({'Status': 'Error'})


@app.route('/db/rebuild', methods=['GET', 'POST'])
def rebuild_database():
    db.drop_all()
    db.create_all()

    teacher = Teacher(
        name = 'Prof Barcelona',
        msisdn = '639183339068'
        )

    student = Student(
        name = 'Jasper Barcelona',
        level = '2nd Grade',
        section = 'Charity',
        msisdn = '639189123947'
        )

    db.session.add(teacher)
    db.session.add(student)
    db.session.commit()

    return SWJsonify({'Status': 'Database Rebuild Success'})


if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']), host='0.0.0.0')

    # port=int(os.environ['PORT']), host='0.0.0.0'