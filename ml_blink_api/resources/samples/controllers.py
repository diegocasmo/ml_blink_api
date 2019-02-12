from flask import Blueprint, jsonify
from ml_blink_api.utils.db import db
from ml_blink_api.utils.beta_samples import insert_beta_samples_in_db
from ml_blink_api.utils.http_status_code import (
  HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY
)

samples = Blueprint('samples', __name__)

@samples.route('', methods=['POST'])
def insert_beta_samples():
  samples = list(db.samples.find())
  # Verify samples collection hasn't already been created
  if len(samples) == 0:
    # TODO: Insert beta samples in a background worker
    insert_beta_samples_in_db()
    return jsonify(), HTTP_201_CREATED
  else:
    return jsonify({'error': 'Beta samples were already inserted in DB'}), HTTP_422_UNPROCESSABLE_ENTITY
