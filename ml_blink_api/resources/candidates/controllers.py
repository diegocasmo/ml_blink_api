from pymongo import ASCENDING
from flask import Blueprint, request, jsonify
from ml_blink_api.config.db import candidates_collection
from ml_blink_api.utils.http_status_code import HTTP_200_OK
from ml_blink_api.models.candidate import generate_random_candidate

candidates = Blueprint('candidates', __name__)

@candidates.route('/best', methods=['GET'])
def get_best_candidate():
  # Initial query will find best candidate among all
  query = {}

  # Allow to exclude image keys when retrieving candidates
  image_keys = request.args.get('exclude_image_keys[]', []).split(',')
  if len(image_keys) > 0 and all(x.isdigit() for x in image_keys):
    query['image_key'] = {'$nin': list(map(lambda x: int(x), image_keys))}

  candidates = list(candidates_collection.find(query).sort('v', ASCENDING))
  if len(candidates) > 0:
    # Remove candidate with the lowest `v` from DB before sending response
    candidates_collection.remove({'_id': candidates[0].get('_id')})
    return jsonify(candidates[0]), HTTP_200_OK
  else:
    # If there's no candidate, pseudo-randomly generate one on the fly
    return jsonify(generate_random_candidate()), HTTP_200_OK
