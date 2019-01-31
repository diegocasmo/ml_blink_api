from flask import Blueprint, request, jsonify
from datetime import datetime
from cerberus import Validator
from ml_blink_api.utils.db import db
from ml_blink_api.models.user import user_schema
from ml_blink_api.utils.auth import encrypt_user_password
from ml_blink_api.utils.http_status_code import (
  HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
)

users = Blueprint('users', __name__)

@users.route('', methods=['POST', 'OPTIONS'])
def create():
  # Validate user attributes
  attrs = request.get_json()
  attrs['created_at'] = datetime.now()
  attrs['updated_at'] = None
  v = Validator(user_schema)
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
