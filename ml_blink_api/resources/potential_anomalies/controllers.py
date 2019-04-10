import json
from bson import ObjectId
from ml_blink_api.utils.flask_logger import log_info
from ml_blink_api.config.db import potential_anomalies_collection
from ml_blink_api.jobs.potential_anomaly import tinsert_in_active_set
from flask import (
  Blueprint, flash, request, redirect, render_template, url_for
)

potential_anomalies = Blueprint('potential_anomalies', __name__)

@potential_anomalies.route('', methods=['GET'])
def index():
  return render_template('potential_anomalies/index.html',
    potential_anomalies = list(potential_anomalies_collection.find())
  )

@potential_anomalies.route('/<str_id>', methods=['GET'])
def show(str_id):
  return render_template('potential_anomalies/show.html',
    potential_anomaly = potential_anomalies_collection.find_one(ObjectId(str_id))
  )

@potential_anomalies.route('/delete', methods=['POST'])
def destroy():
  # Find potential anomaly
  potential_anomaly_id = ObjectId(request.form.get('potential_anomaly_id'))
  potential_anomaly = potential_anomalies_collection.find_one(potential_anomaly_id)

  # Create task to add potential anomaly to active set in the background
  potential_anomaly.pop('_id') # ObjectId isn't serializable, and we don't need it
  tinsert_in_active_set.delay(json.dumps(potential_anomaly))

  # Remove potential anomaly
  potential_anomalies_collection.remove({'_id': potential_anomaly_id})

  flash(u'Successfully removed potential anomaly', 'success')

  return redirect(url_for('potential_anomalies.index'))
