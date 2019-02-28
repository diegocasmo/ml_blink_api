from flask import Blueprint, request, jsonify
from cerberus import Validator
from ml_blink_api.config.db import missions_collection
from ml_blink_api.models.user import get_temp_test_user
from ml_blink_api.models.mission import mission_schema
from ml_blink_api.jobs.process_mission import tprocess_created_mission
from ml_blink_api.utils.http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
)

missions = Blueprint('missions', __name__)

@missions.route('', methods=['GET'])
def get():
  return jsonify(list(missions_collection.find())), HTTP_200_OK

@missions.route('', methods=['POST', 'OPTIONS'])
def create():
  # Assume mission belongs to the temporary test user
  user = get_temp_test_user()
  if user:
    # Validate mission attributes
    v = Validator(mission_schema)
    if v.validate(request.get_json()):
      # Insert valid mission in DB
      mission_id = missions_collection.insert_one(v.document).inserted_id
      if mission_id:
        # Process mission details in the background
        tprocess_created_mission.delay(str(mission_id))
        return jsonify({}), HTTP_201_CREATED
      else:
        return jsonify({}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
      return jsonify(v.errors), HTTP_422_UNPROCESSABLE_ENTITY
  else:
    return jsonify({'error': 'Test user doesn\'t exist'}), HTTP_422_UNPROCESSABLE_ENTITY

@missions.route('/max_accuracy', methods=['GET'])
def max_accuracy():
  # Initial query will return missions mapped by their 'image_key' with max accuracy achieved
  query = {}
  # Allow to filter missions by 'image_key'
  image_key = request.args.get('image_key')
  if image_key and image_key.isdigit():
    query['image_key'] = int(image_key)

  # Map missions by their 'image_key' (if provided) and max 'accuracy' achieved
  missions = missions_collection.aggregate([
    {'$group': {'_id': '$image_key', 'max_accuracy': {'$max':'$accuracy'}}},
    {'$addFields': {'image_key': '$_id'}},
    {'$project': {'_id': 0}},
    {'$match': query}
  ])

  results = list(missions)
  if len(results) == 0:
    # If no mission has such 'image_key', then max accuracy so far achieved is None
    return jsonify({'image_key': query.get('image_key'), 'max_accuracy': None}), HTTP_200_OK
  elif len(results) == 1:
    return jsonify(results[0]), HTTP_200_OK
  else:
    return jsonify(results), HTTP_200_OK
