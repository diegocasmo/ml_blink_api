from pymongo import DESCENDING
from ml_blink_api.config.db import db
from flask import Blueprint, render_template, redirect, url_for
from ml_blink_api.jobs.ml_blink_101 import ml_blink_101_tcrawl_candidates, NUM_PROJ

measurements = Blueprint('measurements', __name__)

@measurements.route('', methods=['GET'])
def index():
  all_measurements = []
  for num_proj in NUM_PROJ:
    time_steps = 0
    if db['time_steps_{}'.format(num_proj)].find().count() > 0:
      time_steps = db['time_steps_{}'.format(num_proj)].find_one({}, sort=[('_id', DESCENDING)]).get('count')

    all_measurements.append({
      'num_proj': num_proj,
      'anomalies': db['anomalies_{}'.format(num_proj)].find().count(),
      'active_set_size': db['active_set_{}'.format(num_proj)].find().count(),
      'time_steps': time_steps,
      'active_set': list(db['active_set_{}'.format(num_proj)].aggregate([
        {'$match': {}},
        {'$project': {'_id': 0, 'image_key': 1, 'usno_band': 1, 'panstarr_band': 1, 'v': 1}}
      ]))
    })

  return render_template('measurements/index.html',
    all_measurements = all_measurements,
    delimiter = 5
  )

@measurements.route('', methods=['POST'])
def new():
  # Drop all collections
  for num_proj in NUM_PROJ:
    db['anomalies_{}'.format(num_proj)].drop()
    db['active_set_{}'.format(num_proj)].drop()
    db['time_steps_{}'.format(num_proj)].drop()

  # Start measurement
  ml_blink_101_tcrawl_candidates.delay()
  return redirect(url_for('measurements.index'))
