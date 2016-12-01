import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from models import *

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# initialize the database
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# working with auth to determine wether a password is correct or incorrect
# it will return true or false depending wether the password is correct or
# incorrect


@auth.verify_password
def verify_password(username, password):
    # getting a user from the database
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    return g.user.verify_password(password)

# protecting all the API endpoints


@app.before_request
@auth.login_required
def before_request():
    pass

# handling an error that occurs because of an incorrect password


@auth.error_handler
def unauthorized():
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': 'please authenticate'})
    response.status_code = 401
    return response
