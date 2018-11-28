# data access object(DAO)

from db import db, User

def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def get_user_by_session_token(session_token):
    return User.query.filter(User.session_token == session_token).first()

def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token == update_token).first()

def verify_credentials(email, userid):
    optional_user = get_user_by_email(email)    #check if the user associate with the email
    
    if optional_user is None:
        return False, None

    return optional_user.verify_userid(userid), optional_user   # also check password

def create_user(email, userid):
    # make the user is not already exist by email
    optional_user = get_user_by_email(email)

    if optional_user is not None:
        return False, optional_user

    user = User(
        email=email,
        userid=userid,
    )

    db.session.add(user)
    db.session.commit()

    return True, user

def renew_session(update_token):
    # whenever the user want to renew the session, they send the update token
    user = get_user_by_update_token(update_token)

    if user is None:
        raise Exception('Invalid update token.')

    user.renew_session()
    db.session.commit()
    return user
    
