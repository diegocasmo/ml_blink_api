from pymongo import ASCENDING
from flask import Blueprint, jsonify
from ml_blink_api.config.db import candidates_collection
from ml_blink_api.models.candidate import generate_random_candidate
from ml_blink_api.utils.http_status_code import HTTP_200_OK

candidates = Blueprint('candidates', __name__)

@candidates.route('/best', methods=['GET'])
def get_best_candidate():
  candidates = list(candidates_collection.find({}).sort('v', ASCENDING))
  if len(candidates) > 0:
    # Retrieve candidate with the lowest `v` of all
    candidate = candidates[0]
    candidates_collection.remove({'_id': candidate.get('_id')})
    return jsonify(candidate), HTTP_200_OK
  else:
    # If there's no candidate, pseudo-randomly generate one on the fly
    return jsonify(generate_random_candidate()), HTTP_200_OK
