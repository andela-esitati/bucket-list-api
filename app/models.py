
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

__all__ = ['User', 'BucketList', 'BucketListItems']


class User(db.Model):
    __tablename__ = 'users'
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

    class BucketList(db.Model):
        __tablename__ = 'bucketlist'
        bucketlist_id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150), nullable=False)
        date_created = db.Column(db.Datetime, default=datetime.now())
        date_modified = db.Column(db.Datetime, default=datetime.now())
        created_by = db.Column(db.Integer, db.ForeignKey('user.user_id',
                                                         ondelete='CASCADE'))
        bucketlistitems = db.relationship('BucketListItems',
                                          backref='bucketlist',
                                          passive_deletes=True)

    class BucketListItems(db.Model):
        __tablename__ = 'bucketlistitems'
        item_id = db.Column(db.Integer, primary_key=True)
        bucketlist_id = db.Column(db.Integer,
                                  db.ForeignKey('bucketlist.bucketlist_id',
                                                ondelete='CASCADE'))
        name = db.Column(db.String(150), nullable=False)
        date_created = db.Column(db.Datetime, default=datetime.now())
        date_modified = db.Column(db.Datetime, default=datetime.now())
        done = db.Column(db.Boolean, default='False')


db.create_all()
