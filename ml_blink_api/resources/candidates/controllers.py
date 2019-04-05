import random
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
    # Select candidate with lowest `v`
    lowest_v = candidates[0].get('v')
    # If there are multiple with same lowest `v` value, randomly select one of those
    candidate = random.choice([c for c in candidates if c.get('v') == lowest_v])
    # Remove selected candidate
    candidates_collection.remove({'_id': candidate.get('_id')})

    return jsonify(candidate), HTTP_200_OK
  else:
    # If there's no candidate, pseudo-randomly generate one on the fly
    return jsonify(generate_random_candidate()), HTTP_200_OK
