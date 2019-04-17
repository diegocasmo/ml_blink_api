import math
from flask import Blueprint, render_template, redirect, url_for
from ml_blink_api.jobs.ml_blink_101 import (
  ml_blink_101_tcrawl_candidates,
  MIN_PROJECTIONS, MAX_PROJECTIONS, EXPONENT
)
from ml_blink_api.config.db import db

measurements = Blueprint('measurements', __name__)

@measurements.route('', methods=['GET'])
def index():
  return render_template('measurements/index.html')

@measurements.route('', methods=['POST'])
def new():
  # Drop all collections
  num_projections = MIN_PROJECTIONS
  while num_projections < MAX_PROJECTIONS:
    db['anomalies_{}'.format(num_projections)].drop()
    db['active_set_{}'.format(num_projections)].drop()
    db['time_steps_{}'.format(num_projections)].drop()
    num_projections = math.floor(math.pow(num_projections, EXPONENT))

  # Start measurement
  ml_blink_101_tcrawl_candidates.delay()
  return redirect(url_for('measurements.index'))
