import numpy as np
from functools import reduce
from ml_blink_api.utils.usno import get_usno_vector
from ml_blink_api.utils.panstarr import get_panstarr_vector
from ml_blink_api.config.celery_config import celery, logger
from ml_blink_api.config.db import candidates_collection, active_set_collection
from ml_blink_api.models.candidate import generate_random_candidate, insert_candidate

@celery.task(name='tgenerate_candidate')
def tgenerate_candidate():
  '''
  Attempt to generate a candidate using the active set vectors
  '''
  try:
    num_candidates = candidates_collection.find({}).count()
    if num_candidates < 25:
      # Generate a potential candidate
      candidate = generate_random_candidate()
      logger.info('`image_key`: {}'.format(candidate.get('image_key')))
      logger.info('`usno_band`: {}'.format(candidate.get('usno_band')))
      logger.info('`panstarr_band`: {}'.format(candidate.get('panstarr_band')))

      # Get USNO and PanSTARRs images' vectors
      A = list(active_set_collection.find({}))
      x = get_usno_vector(candidate.get('image_key'), candidate.get('usno_band'))
      y = get_panstarr_vector(candidate.get('image_key'), candidate.get('panstarr_band'))

      # Compute `v`
      candidate['v'] = compute_v(x, y, A)
      logger.info('`v`: {}'.format(candidate.get('v')))

      # Attempt to insert candidate in DB
      candidate_id = insert_candidate(candidate)
      logger.info('Inserted candidate {} in DB'.format(candidate_id))
    else:
      logger.info('There are {} candidates stored in DB. Skipping...'.format(num_candidates))
  except Exception as e:
    logger.error('Unable to generate candidate: {}'.format(e))

def compute_v(x, y, A):
  '''
  Compute the value of `v` given two vectors `x` (an USNO image vector) and `y` (a PanSTARRs image vector).
  The formula for `v` is `v = x^T * D * y`, where `D` is implicitly represented as `D = sum_{i in A} x_i * y_i^T`
  and `A` is the active set
  '''
  def reduce_A(acc, c):
    '''
    Use `D` implicit representation to compute `v`.
    Example: Given `A = (1,2)`, `v = (x^T * v1) * (y * w1^T) + (x^T * v2)*(y * w2^T)`
    '''
    # Retrieve USNO and PanSTARRs vectors in `c`
    v = get_usno_vector(c.get('image_key'), c.get('usno_band'))
    w = get_panstarr_vector(c.get('image_key'), c.get('panstarr_band'))
    return acc + np.dot(np.dot(np.transpose(x), v), np.dot(y, np.transpose(w)))
  return reduce(reduce_A, A, 0)
