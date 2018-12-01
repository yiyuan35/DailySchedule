import json
from datetime import datetime
from db import db, User, Event
from flask import Flask, request
import users_dao
from google.oauth2 import id_token
from google.auth.transport import requests

db_filename = "calender.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def extract_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return False, json.dumps({'error': 'Missing authorization header.'})
    # Header looks like "Authorization: Bearer <session token>"
    bearer_token = auth_header.replace('Bearer ', '').strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps({'error': 'Invalid authorization header.'})
    return True, bearer_token

@app.route('/register/', methods=['POST'])
def register_account():
    try:
        post_body = json.loads(request.data)
        token = post_body['id_token']

        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "750288393391-qo22436ht2sgrhinj3o3lfsiivsb0s4i.apps.googleusercontent.com")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # return json.dumps(idinfo)
        userid = idinfo['sub']
        email = idinfo['email']

        created, user = users_dao.create_user(email, userid)

        if email is None or userid is None:
            return json.dumps({'error': 'Invalid email or password'})

        if not created:
            return json.dumps({'error': 'User already exists.'})
        
        return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
        })

    except ValueError:
        # return json.dumps({'error': 'Invalid user id'})
        raise ValueError('Invalid Token')

@app.route('/login/', methods=['POST'])
def login():
    try:
        post_body = json.loads(request.data)
        token = post_body['id_token']
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "750288393391-qo22436ht2sgrhinj3o3lfsiivsb0s4i.apps.googleusercontent.com")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # return json.dumps(idinfo)
        userid = idinfo['sub']
        email = idinfo['email']
        # if email is None or userid is None:
        #     return json.dumps({'error': 'Invalid email or password'})

        success, user = users_dao.verify_credentials(email, userid)
        
        if not success:
            return json.dumps({'error': 'Incorrect email or password.'})
        
        return json.dumps({
            'session_token': user.session_token,
            'session_expiration': str(user.session_expiration),
            'update_token': user.update_token
        })

    except ValueError:
        # return json.dumps({'error': 'Invalid user id'})
        raise ValueError('Invalid Token')

@app.route('/session/', methods=['POST'])
def update_session():
    success, update_token = extract_token(request)
    if not success:
         return update_token
    try:
        user = users_dao.renew_session(update_token)
    except: 
        return json.dumps({'error': 'Invalid update token.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token
    })

# @app.route('/secret/', methods=['GET'])
def verify_session():
    success, session_token = extract_token(request)
    if not success:
        return False, session_token 
    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return False
    return True

@app.route('/')
def hello():
    return "Hello World"
    
@app.route('/api/events/', methods=['GET'])
def get_events():
    """ Return all events of the user as a json object """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)

    if user is not None:
        events = [event.serialize() for event in user.events]
        return json.dumps({'success': True, 'data': events}, default=to_serializable), 200
    return json.dumps({'success': False, 'error': 'User not found.'}), 404

def to_serializable(val):
    """ Used by default. """
    return str(val)

@app.route('/api/events/<string:date>/', methods=['GET'])
def get_events_by_date(date):
    """ Return all events for a given date of the user """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)
    # user = User.query.filter_by(id=user_id).first()
    if user is not None:
        search_date = datetime.strptime(date, '%Y-%m-%d')
        events = Event.query.filter_by(date = search_date)
        result = [event.serialize() for event in events]
        return json.dumps({'success': True, 'data': result}, default=to_serializable), 200
    return json.dumps({'success': False, 'error': 'User not found.'}), 404
    
@app.route('/api/events/<string:date>/order/', methods=['GET'])
def get_events_order(date):
    """ Return all events in a descending order for a given date of the user """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)

    if user is not None:
        search_date = datetime.strptime(date, '%Y-%m-%d')
        events = Event.query.filter_by(date = search_date).order_by(Event.priority.desc())
        result = [event.serialize() for event in events]
        return json.dumps({'success': True, 'data': result}, default=to_serializable), 200
    return json.dumps({'success': False, 'error': 'User not found.'}), 404

@app.route('/api/events/', methods=['POST'])
def create_event():
    """ Create an event and return the created event for the user """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)
    if user is not None:
        post_body = json.loads(request.data)
        event = Event(
            title=post_body.get('title'),
            description=post_body.get('description'),
            date=datetime.strptime(post_body.get('date'), '%Y-%m-%d').date(), 
            # startTime=datetime.strptime(post_body.get('startTime'), '%b %d %Y %I:%M%p'), 
            # endTime=datetime.strptime(post_body.get('endTime'), '%b %d %Y %I:%M%p'), 
            location=post_body.get('location'),
            # reminder=datetime.strptime(post_body.get('reminder'), '%b %d %Y %I:%M%p'), 
            priority=post_body.get('priority'),
            user_id=user.userid
        )
        user.events.append(event)
        db.session.add(event)
        db.session.commit()
        return json.dumps({'success': True, 'data': event.serialize()}, default=to_serializable), 201
    return json.dumps({'success': False, 'error': 'User not found!'}), 404 

@app.route('/api/event/<int:event_id>/', methods=['POST'])
def update_event(event_id):
    """ edit an event and return the updated event information """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)
    user_id = user.id
    if user is not None:
        event = Event.query.filter_by(id=event_id, user_id=user_id).first()
        if event is not None:
            post_body = json.loads(request.data)
            event.title = post_body.get('title', event.title)
            event.description = post_body.get('description', event.description)
            event.date = datetime.strptime(post_body.get('date', event.date), '%Y-%m-%d').date()
            # event.startTime = datetime.strptime(post_body.get('startTime', event.startTime), '%b %d %Y %I:%M%p')
            # event.endTime = datetime.strptime(post_body.get('endTime', event.endTime), '%b %d %Y %I:%M%p')
            event.location = post_body.get('location', event.location)
            # event.reminder = datetime.strptime(post_body.get('reminder', event.reminder), '%b %d %Y %I:%M%p')
            event.priority = post_body.get('priority', event.priority)
            event.user_id = user_id
            db.session.commit()
            return json.dumps({'success': True, 'data': event.serialize()}, default=to_serializable), 200
        return json.dumps({'success': False, 'error': 'Event not found!'}), 404
    return json.dumps({'success': False, 'error': 'User not found!'}), 404

@app.route('/api/event/<int:event_id>/', methods=['DELETE'])
def delete_event(event_id):
    """ delete an event and return the deleted event  """
    valid = verify_session()
    if not valid:
        return json.dumps({'success': False, 'error':'Invalid session_token'})
    success, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)
    user_id = user.id
    if user is not None:
        event = Event.query.filter_by(id=event_id, user_id=user_id).first() 
        if event is not None:
            db.session.delete(event)
            db.session.commit()
            return json.dumps({'success': True, 'data': event.serialize()}, default=to_serializable), 200
        return json.dumps({'success': False, 'error': 'Event not found!'}), 404 
    return json.dumps({'success': False, 'error': 'User not found!'}), 404 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
