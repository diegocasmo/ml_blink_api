from pymongo import DESCENDING
from flask import Blueprint, request, jsonify
from cerberus import Validator
from ml_blink_api.config.db import comments_collection
from ml_blink_api.models.user import get_temp_test_user
from ml_blink_api.models.comment import comment_schema
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY,
  HTTP_500_INTERNAL_SERVER_ERROR
)

comments = Blueprint('comments', __name__)

@comments.route('', methods=['GET'])
def get():
  # Initial query will retrieve all comments
  query = {}
  # Allow to filter comments by 'image_key'
  image_key = request.args.get('image_key')
  if image_key and image_key.isdigit():
    query['image_key'] = int(image_key)
  comments = comments_collection.aggregate([
    {'$lookup': {'from': 'users', 'localField': 'user_id', 'foreignField': '_id', 'as': 'user'}},
    {'$unwind': '$user'},
    {'$match': query},
    {
      # Remove private user attributes
      '$project': {'user.created_at': 0, 'user.email': 0, 'user.password': 0, 'user.salt': 0}
    },
    {'$sort': {'created_at': DESCENDING}}
  ])
  return jsonify(list(comments)), HTTP_200_OK

@comments.route('', methods=['POST', 'OPTIONS'])
def create():
  # Assume comment belongs to the temporary test user
  user = get_temp_test_user()
  if user:
    # Validate comment attributes
    v = Validator(comment_schema)
    if v.validate(request.get_json()):
      attrs = v.document
      # Insert valid comment in DB
      if comments_collection.insert_one(attrs).inserted_id:
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    return jsonify({'error': 'Test user doesn\'t exist'}), HTTP_422_UNPROCESSABLE_ENTITY
