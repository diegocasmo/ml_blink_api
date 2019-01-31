from flask import Blueprint, request, jsonify
from cerberus import Validator
from ml_blink_api.utils.db import db
from ml_blink_api.models.user import get_test_user
from ml_blink_api.models.matching import schema
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY,
  HTTP_500_INTERNAL_SERVER_ERROR
)

matchings = Blueprint('matchings', __name__)

@matchings.route('', methods=['GET'])
def get():
  return jsonify(list(db.matchings.find())), HTTP_200_OK

@matchings.route('', methods=['POST', 'OPTIONS'])
def create():
  attrs = request.get_json()
  # Assume matching belongs to the temporary test user
  user = get_test_user()
  if user:
    # Assign matching to user and validate it
    attrs['user_id'] = str(user.get('_id'))
    v = Validator(schema)
    if v.validate(attrs):
      # Insert valid matching in DB
      if db.matchings.insert_one(attrs).inserted_id:
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    return jsonify({'error': 'Test user doesn\'t exist'}), HTTP_422_UNPROCESSABLE_ENTITY
