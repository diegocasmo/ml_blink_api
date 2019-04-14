from pymongo import DESCENDING
from flask import Blueprint, render_template, redirect, url_for
from ml_blink_api.jobs.ml_blink_101 import MAX_TIME_STEPS, ml_blink_101_tcrawl_candidates
from ml_blink_api.config.db import active_set_collection, anomalies_collection, time_steps_collection

measurements = Blueprint('measurements', __name__)

@measurements.route('', methods=['GET'])
def index():
  last_time_step = time_steps_collection.find_one({}, sort=[('_id', DESCENDING)])
  return render_template('measurements/index.html',
    max_time_steps = MAX_TIME_STEPS,
    curr_time_steps = last_time_step.get('count') if last_time_step else 0,
    anomalies = list(anomalies_collection.find()),
    active_set = list(active_set_collection.find()),
    active_set_delimeter = 20
  )

@measurements.route('', methods=['POST'])
def new():
  # Clear everything
  active_set_collection.remove({})
  anomalies_collection.remove({})
  time_steps_collection.remove({})

  # Start measurement
  ml_blink_101_tcrawl_candidates.delay()

  return redirect(url_for('measurements.index'))
