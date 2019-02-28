from bson import ObjectId
from ml_blink_api.config.celery_config import celery, logger
from ml_blink_api.config.db import missions_collection, active_set_collection
from ml_blink_api.models.candidate import has_expected_dim

@celery.task(name='tprocess_created_mission')
def tprocess_created_mission(mission_id):
  '''
  Insert a mission's candidate to the active set if its accuracy is at least equal to the mission's accuracy threshold
  '''
  try:
    # Find recently created mission
    mission = missions_collection.find_one({'_id': ObjectId(mission_id)})
    if not mission: raise ValueError('Mission with id {} doesn\'t exist'.format(mission_id))

    # Add mission's details to active set if successfully completed
    if mission.get('accuracy') >= mission.get('accuracy_threshold'):
      attrs = {
        'image_key': mission.get('image_key'),
        'usno_band': mission.get('image_one').get('band'),
        'panstarr_band': mission.get('image_two').get('band')
      }
      # Make sure mission's candidate has correct dimensions
      if not has_expected_dim(attrs): raise ValueError('Mission with id {} candidate has incorrect dimensions'.format(mission_id))

      # Insert mission's candidate in active set
      member_id = active_set_collection.insert_one(attrs).inserted_id
      logger.info('Inserted member with id {} in active set'.format(member_id))
    else:
      logger.info('Mission with id {} was not successfully completed'.format(mission_id))
  except Exception as e:
    logger.error('Unable to process created mission: {}'.format(e))
