import bcrypt
from functools import wraps
from flask import session, jsonify
from api.utils.http_status_code import HTTP_401_UNAUTHORIZED

def encrypt_user_password(user):
  '''
  Given a user, augment its attributes with a salt and a password (hashed)
  with that salt
  '''
  user['salt'] = bcrypt.gensalt()
  password = user['password']
  user['password'] = bcrypt.hashpw(password, user['salt'])
  return user


def password_matches(user, password):
  '''
  Return true if a user password matches the argument `password`, false otherwise
  '''
  return bcrypt.hashpw(password, user['salt']) == user['password']

def requires_auth(f):
  '''
  A decorator that can be used to wrap routes which require a user to be authenticated.
  Returns 401 if the user does not have a session
  '''
  @wraps(f)
  def decorated(*args, **kwargs):
    if not 'user_id' in session:
      return jsonify({}), HTTP_401_UNAUTHORIZED
    return f(*args, **kwargs)
  return decorated

def requires_unauth(f):
  '''
  A decorator that can be used to wrap routes which require a user to be UNauthenticated.
  Returns 401 if the user HAS a session
  '''
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'user_id' in session:
      return jsonify({}), HTTP_401_UNAUTHORIZED
    return f(*args, **kwargs)
  return decorated
