import numpy as np
from bson import ObjectId
from functools import reduce
from ml_blink_api.utils.usno import get_usno_vector
from ml_blink_api.utils.panstarr import get_panstarr_vector
from ml_blink_api.config.celery_config import celery, logger
from ml_blink_api.config.db import missions_collection, candidates_collection, active_set_collection
from ml_blink_api.models.candidate import generate_random_candidate, has_expected_dim, insert_candidate

@celery.task
def process_created_mission(mission_id):
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

@celery.task
def generate_candidate():
  '''
  Attempt to generate a candidate using the active set vectors
  '''
  try:
    num_candidates = candidates_collection.find({}).count()
    if num_candidates < 10:
      # Generate a potential candidate
      candidate = generate_random_candidate()
      logger.info('Candidate `image_key`: {}'.format(candidate.get('image_key')))
      logger.info('Candidate `usno_band`: {}'.format(candidate.get('usno_band')))
      logger.info('Candidate `panstarr_band`: {}'.format(candidate.get('panstarr_band')))

      # Get USNO and PanSTARRs images' vectors
      usno_vector = get_usno_vector(candidate.get('image_key'), candidate.get('usno_band'))
      panstarr_vector = get_panstarr_vector(candidate.get('image_key'), candidate.get('panstarr_band'))

      # Compute `v`
      v = compute_v(usno_vector, panstarr_vector)
      logger.info('`v` value: {}'.format(v))

      # Attempt to insert candidate in DB
      candidate_id = insert_candidate(v, candidate)
      logger.info('Inserted candidate {} in DB'.format(candidate_id))
    else:
      logger.info('There are {} candidates stored in DB. Skipping...'.format(num_candidates))
  except Exception as e:
    logger.error('Unable to generate candidate: {}'.format(e))

def normalize(xs):
  '''
  Return vector `xs` normalized using the L2 norm
  '''
  return xs/np.linalg.norm(xs, 2)

def compute_v(x, y):
  '''
  Compute the value of `v` given two vectors `x` (an USNO image vector) and `y` (a PanSTARRs image vector).
  The formula for `v` is `v = x^T * D * y`, where `D` is implicitly represented as `D = sum_{i in A} x_i * y_i^T`
  and `A` is the active set
  '''
  A = list(active_set_collection.find({}))
  x = normalize(x)
  y = normalize(y)
  def reduce_v(x, y, acc, c):
    '''
    Use `D` implicit representation to compute `v`.
    Example: Given `A = (1,2)`, `v = (x^T * v1) * (y * w1^T) + (x^T * v2)*(y * w2^T)`
    '''
    # Retrieve USNO and PanSTARRs vectors in `c`
    usno_vector = get_usno_vector(c.get('image_key'), c.get('usno_band'))
    panstarr_vector = get_panstarr_vector(c.get('image_key'), c.get('panstarr_band'))
    # Make sure `v` and `w` are normalized
    v = normalize(usno_vector)
    w = normalize(panstarr_vector)
    # Compute
    xT_v = np.dot(np.transpose(x), normalize(v))
    y_wT = np.dot(y, np.transpose(normalize(w)))
    return acc + np.dot(xT_v, y_wT)
  return reduce(lambda acc, c: reduce_v(x, y, acc, c), A, 0)
