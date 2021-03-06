from flask import Blueprint, render_template
from ml_blink_api.config.db import (
  active_set_collection, candidates_collection, potential_anomalies_collection
)

crawl = Blueprint('crawl', __name__)

@crawl.route('', methods=['GET'])
def index():
  return render_template('crawl/index.html',
    active_set = list(active_set_collection.find()),
    candidates = list(candidates_collection.find()),
    potential_anomalies = list(potential_anomalies_collection.find()))
