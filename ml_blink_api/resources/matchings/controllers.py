from flask import Blueprint, session, request, jsonify
from cerberus import Validator
from ml_blink_api.utils.db import db
from bson import ObjectId
from ml_blink_api.models.matching import schema, serialize
from ml_blink_api.utils.auth import requires_auth
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY,
  HTTP_500_INTERNAL_SERVER_ERROR
)

matchings = Blueprint('matchings', __name__)

@matchings.route('', methods=['GET'])
def get():
  matchings = db.matchings.find()
  return jsonify([serialize(x) for x in matchings]), HTTP_200_OK

@matchings.route('', methods=['POST', 'OPTIONS'])
@requires_auth
def create():
  # Get attributes from request
  attrs = {
    'user_id': session['user_id'],
    'accuracy': float(request.form.get('accuracy', None))
  }
  # Validate matching attributes
  v = Validator(schema)
  if v.validate(attrs):
    # Make user exists in DB
    user = db.users.find_one({'_id': ObjectId(attrs.get('user_id'))})
    if user:
      # Insert matching in DB
      if db.matchings.insert_one(attrs).inserted_id:
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return jsonify({'user_id': 'User does not exist'}), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
