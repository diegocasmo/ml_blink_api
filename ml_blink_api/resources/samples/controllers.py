from flask import Blueprint, request, jsonify
from ml_blink_api.config.db import samples_collection
from ml_blink_api.utils.http_status_code import HTTP_201_CREATED, HTTP_200_OK
from ml_blink_api.jobs.tasks import insert_beta_samples_in_db

samples = Blueprint('samples', __name__)

@samples.route('', methods=['GET'])
def get():
  # Retrieve query parameters
  per_page_query = request.args.get('per_page')
  page_num_query = request.args.get('page_num')

  # Use query parameters for pagination if provided, defaults otherwise
  per_page = int(per_page_query) if per_page_query and per_page_query.isdigit() else 10
  page_num = int(page_num_query) if page_num_query and page_num_query.isdigit() else 0

  samples = samples_collection.find().skip(page_num).limit(per_page)
  return jsonify(list(samples)), HTTP_200_OK

@samples.route('', methods=['POST'])
def insert_beta_samples():
  # Verify samples collection hasn't already been created
  if samples_collection.find().count() == 0:
    task = insert_beta_samples_in_db.apply_async()
    return jsonify({'message': 'Task {}, to insert the beta samples in DB, has been created in the task queue'.format(task.id)}), HTTP_201_CREATED
  else:
    return jsonify({'message': 'Beta samples were already inserted in DB'}), HTTP_200_OK
