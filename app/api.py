import os
from flask import Flask, jsonify, request
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from models import *

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
db = SQLAlchemy(app)
auth = HTTPTokenAuth(scheme='Token')
# auth = HTTPBasicAuth()
# creating a blueprint for all routes authenticated by python
# api = Blueprint('api', __name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

current_user = {
    'user_id': None
}


@auth.verify_token
def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        # The token is valid but has expired
        return None
    except BadSignature:
        # The token is invalid
        return None
    user_id = data['id']
    current_user['user_id'] = user_id
    return user_id


@app.errorhandler(404)
def invalid_url(error):
    return jsonify({'message': 'You entered an invalid URL'})


@app.errorhandler(401)
def token_expired_or_invalid(error):
    return jsonify({'message': 'Token Expired/Invalid'})


def verify_password(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return user
# function that requests tokens


# @app.route('/get-auth-token')
# @auth.login_required
# def get_auth_token():
#     return jsonify({'token': g.user.generate_auth_token()})


@app.route('/auth/register', methods=['POST'])
def register_new_user():
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    # check if username or password are provided
    if not username.strip() or not password.strip():
        return jsonify({'message': 'Username/Passwords Not Provided!'})

    # Check if the username already exists
    if db.session.query(User).filter_by(username=username).first() is not None:
        user = db.session.query(User).filter_by(username=username).first()
        return jsonify({'message': 'User already exists!'})

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error occured while adding user'})
    return jsonify({
        'user': user.username,
        'message': 'login endpoint: localhost:5000/auth/login'
    }), status.HTTP_201_CREATED


@app.route('/auth/login', methods=['POST'])
def login_user():
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    # check if username or password are provided
    if not username.strip() or not password.strip():
        return jsonify({'message': 'Username/Password Not Provided!'})

    user = verify_password(username, password)
    if user:
        token = user.generate_auth_token()
        return jsonify({
            'message': 'Hello, {0}'.format(user.username),
            'token': 'Token ' + token.decode('ascii')
        })
    else:
        return jsonify({'message': 'invalid username/passwprd'})


@app.route('/bucketlists', methods=['POST'])
@auth.login_required
def create_bucketlist():
    user_id = current_user['user_id']
    name = request.json.get('name', '')

    if not name.strip():
        return jsonify({'message': 'bucketlist name not provided'})

    if db.session.query(BucketList).filter_by(name=name,
                                              created_by=user_id).first() is not None:
        return jsonify({'message': 'bucketlist already exists'})

    bucketlist = BucketList(name=name, created_by=user_id)
    db.session.add(bucketlist)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            'message': 'error occured while creating bucketlist'}), status.HTTP_500_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'created bucketlist: {0}'.format(name)}), status.HTTP_201_CREATED

if __name__ == '__main__':
    app.run(debug=True)
