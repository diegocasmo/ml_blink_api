from flask import Blueprint, request, jsonify
from cerberus import Validator
from ml_blink_api.utils.db import db
from ml_blink_api.models.user import schema
from ml_blink_api.utils.auth import encrypt_user_password, requires_unauth
from ml_blink_api.utils.http_status_code import (
  HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
)

users = Blueprint('users', __name__)

@users.route('', methods=['POST', 'OPTIONS'])
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
    # Make sure user email is unique
    user = db.users.find_one({'email': attrs.get('email')})
    if user:
      return jsonify({'email': 'Email must be unique'}), HTTP_422_UNPROCESSABLE_ENTITY
    else:
      # Insert user in DB with hashed password
      if db.users.insert_one(encrypt_user_password(attrs)).inserted_id:
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
  else:
    return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
