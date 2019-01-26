from flask import Blueprint, request, session, jsonify
from cerberus import Validator
from ml_blink_api.db import db
from ml_blink_api.models.user import schema, serialize
from ml_blink_api.utils.auth import (
  password_matches, requires_auth, requires_unauth
)
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED
)

sessions = Blueprint('sessions', __name__)

@sessions.route('', methods=['POST', 'OPTIONS'])
@requires_unauth
def create():
  # Get attributes from request
  attrs = {
    'email': request.form.get('email', None),
    'password': request.form.get('password', None)
  }
  # Validate user attributes
  v = Validator(schema)
  if v.validate(attrs):
    # Find user in DB
    user = db.users.find_one({'email': attrs.get('email')})
    # Verify user password matches
    if user and password_matches(user, attrs.get('password')):
      session['user_id'] = str(user['_id'])
      return jsonify(serialize(user)), HTTP_200_OK
    else:
      return jsonify({}), HTTP_401_UNAUTHORIZED
  else:
    return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY

@sessions.route('', methods=['DELETE', 'OPTIONS'])
@requires_auth
def delete():
  if 'user_id' in session:
    session.pop('user_id')
    return jsonify({}), HTTP_200_OK
  else:
    return jsonify({}), HTTP_401_UNAUTHORIZED
