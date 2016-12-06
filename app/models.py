
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), index=True)
    password_hash = db.Column(db.String(135))
    bucketlists = db.relationship('BucketList',
                                  backref='',
                                  passive_deletes=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # generating token
    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    # decrypting the token and extracting information
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        # anything that is not accepted
        except:
            return None
        # the id identifies the user if the token is valid
        return User.query.get(data['user_id'])


db.create_all()
