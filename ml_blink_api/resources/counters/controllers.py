from flask import Blueprint, jsonify
from pymongo import DESCENDING
from ml_blink_api.config.db import db
from ml_blink_api.utils.http_status_code import HTTP_200_OK

counters = Blueprint('counters', __name__)

@counters.route('', methods=['GET'])
def get():
  counters = db.counters.find({}, sort=[('_id', DESCENDING)])
  return jsonify(list(counters)), HTTP_200_OK
