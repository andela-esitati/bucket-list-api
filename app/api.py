import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# initialize the database
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
