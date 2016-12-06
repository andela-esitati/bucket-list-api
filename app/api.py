import os
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import Flask, url_for, jsonify, request, g, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from models import *

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
# creating a blueprint for all routes authenticated by python
api = Blueprint('api', __name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# initialize the database
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()

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


# handling an error that occurs because of an incorrect password


@auth.error_handler
def unauthorized():
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': 'please authenticate'})
    response.status_code = 401
    return


@auth_token.verify_password
# token will come in place of username
# unused beacuse we are not using password
def verify_auth_token(token, unused):
    g.user = User.verify_auth_token(token)
    return g.user is not None

# error handler for aunauthorised token


@auth_token.error_handler
def unauthorized_token():
    response = jsonify({'status': 401, 'error': 'unauthorizes',
                        'message': 'please send your authentication token'})
    response.status_code = 401
    return response


@api.before_request
@auth_token.login_required
def before_request():
    pass

# function that requests tokens


@app.route('/get-auth-token')
@auth.login_required
def get_auth_token():
    return jsonify({'token': g.user.generate_auth_token()})


# registering blue print
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)
