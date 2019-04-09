from bson import ObjectId
from ml_blink_api.config.celery_config import celery
from ml_blink_api.jobs.crawl import tcrawl_candidates
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.models.mission import matching_has_overlap
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.utils.celery_logger import log_info, log_error
from ml_blink_api.models.candidate import get_candidate_from_mission, has_expected_dim
from ml_blink_api.config.db import missions_collection, active_set_collection, potential_anomalies_collection

@celery.task(name='tprocess_created_mission')
def tprocess_created_mission(str_mission_id):
  '''
  Insert a mission's candidate to the active set if its accuracy is at least equal to the
  mission's accuracy threshold
  '''
  try:
    # Find recently created mission
    mission = missions_collection.find_one({'_id': ObjectId(str_mission_id)})
    if not mission: raise ValueError('Mission with id {} doesn\'t exist'.format(str_mission_id))

    # Make sure the mission's accuracy is valid and matching images overlap
    if mission.get('is_accuracy_valid', False) and matching_has_overlap(mission):
      # Retrieve mission's candidate and validate its dimensions
      attrs = get_candidate_from_mission(mission)
      if not has_expected_dim(attrs): raise ValueError('Mission with id {} candidate has invalid dimensions'.format(str_mission_id))

      # Add mission's details to active set if successfully completed, create potential anomaly otherwise
      if mission.get('accuracy') >= mission.get('accuracy_threshold'):
        attrs['usno_vector'] = get_usno_projection(attrs.get('image_key'), attrs.get('usno_band')).tolist()
        attrs['panstarr_vector'] = get_panstarr_projection(attrs.get('image_key'), attrs.get('panstarr_band')).tolist()
        member_id = active_set_collection.insert_one(attrs).inserted_id
        log_info('Inserted member with id {} in active set'.format(member_id))
        # Run crawler as a new member has been inserted in the active set
        task = tcrawl_candidates.delay()
        log_info('Created crawl task with id: {}'.format(task.id))
      else:
        potential_anomaly_id = potential_anomalies_collection.insert_one(attrs).inserted_id
        log_info('Inserted potential anomaly with id {} in DB'.format(potential_anomaly_id))
    else:
      log_info('Ignored mission with id {}'.format(str_mission_id))
  except Exception as e:
    log_error('Unable to process created mission: {}'.format(e))
