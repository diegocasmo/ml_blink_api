import json
from ml_blink_api.config.celery_config import celery
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.config.db import active_set_collection
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.utils.celery_logger import log_info, log_error

@celery.task(name='tinsert_in_active_set')
def tinsert_in_active_set(potential_anomaly_as_str):
  '''
  Insert a potential anomaly in the active set collection
  '''
  try:
    # Retrieve potential anomaly
    potential_anomaly = json.loads(potential_anomaly_as_str)

    # Extend its attributes with the pre-processed USNO and PanSTARR vectors
    potential_anomaly['usno_vector'] = get_usno_projection(
      potential_anomaly.get('image_key'),
      potential_anomaly.get('usno_band')
    ).tolist()
    potential_anomaly['panstarr_vector'] = get_panstarr_projection(
      potential_anomaly.get('image_key'),
      potential_anomaly.get('panstarr_band')
    ).tolist()

    # Insert 'anomaly' in the active set
    member_id = active_set_collection.insert_one(potential_anomaly).inserted_id
    log_info('Inserted member with id {} in active set'.format(member_id))
  except Exception as e:
    log_error('Unable to insert potential anomaly in the active set: {}'.format(e))
