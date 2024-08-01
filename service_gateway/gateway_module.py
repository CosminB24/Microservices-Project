from flask import *
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *

from flask_login import current_user, login_user, logout_user, UserMixin, LoginManager
from wtforms import *
from flask_session import Session
from decouple import config


import json
import os
import logging
import datetime
import time

from requests import get as Get
from requests import post as Post
from requests import put as Put
from requests import delete as Delete

from microskel.db_module import Base


events_url = config('EVENTS_SERVICE_URL') #nu ii dam alternative, daca nu gaseste -> crapa
weather_url = config('WEATHER_SERVICE_URL')
req_mapping = {'GET': Get, 'PUT': Put, 'POST': Post, 'DELETE' : Delete}


def proxy_request(request, target_url):
    req = req_mapping[request.method]
    kwargs = {'url': target_url, 'params': request.args}
    if request.method in ['PUT', 'POST']:
        kwargs['data'] = dict(request.form)
    response = req(**kwargs).json()
    return json.dumps(response)


def configure_views(app):
    @app.route("/citybreak", methods=["GET"])
    def get():
        city = request.args.get('city')
        date = request.args.get('date', str(datetime.date.today()))
        if not city or not date:
            return 'Invalid request: city or date are missing', 400
        print(f'EVENTS_URL = {events_url}?city={city}&date={date}')
        print(f'WEATHER_URL = {weather_url}?city={city}&date={date}')
        events = Get(f'{events_url}?city={city}&date={date}', verify=False).json()
        weather = Get(f'{weather_url}?city={city}&date={date}', verify=False).json()
        return {'events': events, 'weather': weather}, 200

    @app.route('/events', methods=['POST', 'PUT', 'DELETE'])
    def events():
        return proxy_request(request, events_url)

    @app.route('/weather', methods=['POST', 'PUT', 'DELETE'])
    def weather():
        return proxy_request(request, weather_url)