from flask import Blueprint, jsonify, render_template
from celery.result import AsyncResult
from ml_blink_api.jobs.crawl import tcrawl_candidates
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.config.db import (
  active_set_collection, candidates_collection, missions_collection, anomalies_collection
)

crawl = Blueprint('crawl', __name__)

@crawl.route('', methods=['GET'])
def get():
  task = tcrawl_candidates.delay()
  return render_template('crawler/crawl.html',
    task_id = task.id)

@crawl.route('details', methods=['GET'])
def details():
  return render_template('crawler/details.html',
    active_set = list(active_set_collection.find()),
    candidates = list(candidates_collection.find()),
    anomalies = list(anomalies_collection.find()))

@crawl.route('/clear', methods=['GET'])
def clear():
  return render_template('crawler/clear.html',
    num_active_set_removed = active_set_collection.remove({})['n'],
    num_candidates_removed = candidates_collection.remove({})['n'],
    num_missions_removed = missions_collection.remove({})['n'],
    num_anomalies_removed = anomalies_collection.remove({})['n'])

@crawl.route('/setup', methods=['GET'])
def setup():
  # Define candidates to be inserted in active set
  candidates = [{
    'image_key': 0, 'usno_band': 'blue1', 'panstarr_band': 'g',
    'usno_vector': get_usno_projection(0, 'blue1').tolist(),
    'panstarr_vector': get_panstarr_projection(0, 'g').tolist()
  }, {
    'image_key': 56, 'usno_band': 'blue2', 'panstarr_band': 'g',
    'usno_vector': get_usno_projection(56, 'blue2').tolist(),
    'panstarr_vector': get_panstarr_projection(56, 'g').tolist()
  }, {
    'image_key': 432, 'usno_band': 'red2', 'panstarr_band': 'r',
    'usno_vector': get_usno_projection(432, 'red2').tolist(),
    'panstarr_vector': get_panstarr_projection(432, 'r').tolist()
  }, {
    'image_key': 987, 'usno_band': 'red2', 'panstarr_band': 'r',
    'usno_vector': get_usno_projection(987, 'red2').tolist(),
    'panstarr_vector': get_panstarr_projection(987, 'r').tolist()
  }, {
    'image_key': 501, 'usno_band': 'ir', 'panstarr_band': 'z',
    'usno_vector': get_usno_projection(501, 'ir').tolist(),
    'panstarr_vector': get_panstarr_projection(501, 'z').tolist()
  }]

  # Insert candidates bulk in active set
  active_set_collection.insert_many(candidates)

  return render_template('crawler/details.html',
    active_set = list(active_set_collection.find()),
    candidates = list(candidates_collection.find()),
    anomalies = list(anomalies_collection.find()))
