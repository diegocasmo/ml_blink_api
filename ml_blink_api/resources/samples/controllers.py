from flask import Blueprint, request, jsonify
from ml_blink_api.utils.db import db
from ml_blink_api.utils.http_status_code import HTTP_200_OK

samples = Blueprint('samples', __name__)

@samples.route('', methods=['GET'])
def get():
  # Retrieve query parameters
  per_page_query = request.args.get('per_page')
  page_num_query = request.args.get('page_num')

  # Use query parameters for pagination if provided, defaults otherwise
  per_page = int(per_page_query) if per_page_query and per_page_query.isdigit() else 10
  page_num = int(page_num_query) if page_num_query and page_num_query.isdigit() else 0

  samples = db.samples.find().skip(page_num).limit(per_page)
  return jsonify(list(samples)), HTTP_200_OK
