import os
from flask import Blueprint, request, jsonify
from cerberus import Validator
from ml_blink_api.config.db import db
from ml_blink_api.models.user import user_schema, get_temp_test_user
from ml_blink_api.utils.auth import encrypt_user_password
from ml_blink_api.utils.http_status_code import (
  HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
)

users = Blueprint('users', __name__)

@users.route('', methods=['POST', 'OPTIONS'])
def create():
  user = get_temp_test_user()
  if user:
    return jsonify({'error': 'Temporary test user already exists'}), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    # Validate user attributes
    v = Validator(user_schema)
    if v.validate(request.get_json()):
      attrs = v.document
      # Make sure it's the temporary test user
      if attrs.get('email') == os.getenv('TEMP_TEST_USER_EMAIL'):
        # Insert user in DB with hashed password
        if db.users.insert_one(encrypt_user_password(attrs)).inserted_id:
          return jsonify({}), HTTP_201_CREATED
        else:
          return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
      else:
        return jsonify({'error': 'Invalid temporary test user'}), HTTP_422_UNPROCESSABLE_ENTITY
    else:
      return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
