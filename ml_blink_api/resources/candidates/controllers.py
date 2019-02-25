from pymongo import ASCENDING
from flask import Blueprint, jsonify
from ml_blink_api.config.db import candidates_collection
from ml_blink_api.models.candidate import generate_random_candidate
from ml_blink_api.utils.http_status_code import HTTP_200_OK

candidates = Blueprint('candidates', __name__)

@candidates.route('/oldest', methods=['GET'])
def get_oldest_candidate():
  candidates = list(candidates_collection.find().sort('_id', ASCENDING))
  if len(candidates) > 0:
    # Candidates served to the client are immediately removed from DB
    candidates_collection.remove({'_id': candidates[0].get('_id')})
    return jsonify(candidates[0]), HTTP_200_OK
  else:
    # If there's no candidate, pseudo-randomly generate one on the fly
    return jsonify(generate_random_candidate()), HTTP_200_OK
