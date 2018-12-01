from flask_sqlalchemy import SQLAlchemy
import datetime
import bcrypt
import hashlib
import datetime
import os

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # User information
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)
 
    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)
    # cascade='delete' => when an user is deleted, delete all event
    events = db.relationship('Event', cascade='delete')

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        # takes input for password nad encodes
        # self.password_digest = bcrypt.hashpw(kwargs.get('password').encode('utf8'),
        #                                     bcrypt.gensalt(rounds=13))
        self.password_digest = bcrypt.hashpw(kwargs.get('password').encode('utf8'),
                                            bcrypt.gensalt(rounds=13))
        self.renew_session()

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()
        # helper function to generate tokens

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + \
                                datetime.timedelta(days=1) #can motify the expiration date
        self.update_token = self._urlsafe_base_64()

    # def verify_password(self, password):
    #     # check password given with the encypted password
    #     return bcrypt.checkpw(password.encode('utf8'),
    #                           self.password_digest)

    def verify_password(self, password):
        # check password given with the encypted password
        return bcrypt.checkpw(password.encode('utf8'),
                              self.password_digest)


    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return session_token == self.session_token and \
            datetime.datetime.now() < self.session_expiration   #check not expired
            
    def verify_update_token(self, update_token):
        return update_token == self.update_token


class Event(db.Model):
    __tablename__ = 'event' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    # startTime = db.Column(db.DateTime, nullable=False)
    # endTime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String, nullable=True)
    # reminder = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        # if a title was given in parameter, then use the value or initial value which is ''
        self.description = kwargs.get('description', '')
        self.date = kwargs.get('date', '')
        # self.startTime = kwargs.get('startTime', '')
        # self.endTime = kwargs.get('endTime', '')
        self.location = kwargs.get('location', '')
        # self.reminder = kwargs.get('reminder', '')
        self.priority = kwargs.get('priority', 1)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            # 'startTime': self.startTime,
            # 'endTime': self.endTime,
            'location': self.location,
            # 'reminder': self.reminder,
            'priority': self.priority
        }
