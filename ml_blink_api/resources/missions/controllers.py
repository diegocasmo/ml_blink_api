from flask import Blueprint, request, jsonify
from datetime import datetime
from cerberus import Validator
from ml_blink_api.utils.db import db
from ml_blink_api.models.user import get_temp_test_user
from ml_blink_api.models.mission import mission_schema
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY,
  HTTP_500_INTERNAL_SERVER_ERROR
)

missions = Blueprint('missions', __name__)

@missions.route('', methods=['GET'])
def get():
  return jsonify(list(db.missions.find())), HTTP_200_OK

@missions.route('', methods=['POST', 'OPTIONS'])
def create():
  attrs = request.get_json()
  # Assume mission belongs to the temporary test user
  user = get_temp_test_user()
  if user:
    # Assign mission to user and validate it
    attrs['user_id'] = str(user.get('_id'))
    attrs['created_at'] = datetime.now()
    attrs['updated_at'] = None
    v = Validator(mission_schema)
    if v.validate(attrs):
      # Insert valid mission in DB
      if db.missions.insert_one(attrs).inserted_id:
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    return jsonify({'error': 'Test user doesn\'t exist'}), HTTP_422_UNPROCESSABLE_ENTITY
