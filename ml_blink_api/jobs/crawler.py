import math
import json
import numpy as np
import multiprocessing
from celery import chord
from functools import reduce
from ml_blink_api.utils.usno import get_usno_vector
from ml_blink_api.utils.panstarr import get_panstarr_vector
from ml_blink_api.config.celery_config import celery, logger
from ml_blink_api.config.db import candidates_collection, active_set_collection
from ml_blink_api.models.candidate import generate_random_candidate, insert_candidate

@celery.task(name='tcompute_v')
def tcompute_v(candidate, A):
  '''
  Compute the value of `v` given a candidate. The formula for `v` is `v = x^T * D * y`, where `D` is implicitly
  represented as `D = sum_{i in A} x_i * y_i^T` and `A` is the active set
  '''
  # Get USNO and PanSTARRs images' vectors
  candidate = json.loads(candidate)
  x = get_usno_vector(candidate.get('image_key'), candidate.get('usno_band'))
  y = get_panstarr_vector(candidate.get('image_key'), candidate.get('panstarr_band'))

  def reduce_A(acc, c):
    '''
    Use `D` implicit representation to compute `v`.
    Example: Given `A = (1,2)`, `v = (x^T * v1) * (y * w1^T) + (x^T * v2)*(y * w2^T)`
    '''
    v = get_usno_vector(c.get('image_key'), c.get('usno_band'))
    w = get_panstarr_vector(c.get('image_key'), c.get('panstarr_band'))
    return acc + np.dot(np.dot(np.transpose(x), v), np.dot(y, np.transpose(w)))

  return reduce(reduce_A, A, 0)

@celery.task(name='thandle_compute_v_finished')
def thandle_compute_v_finished(results, candidate):
  '''
  Create a candidate in DB given the result of each individual process computation
  '''
  try:
    # Reduce `v` from each parallel task result
    candidate = json.loads(candidate)
    candidate['v'] = sum(results)
    logger.info('`v`: {}'.format(candidate.get('v')))

    # Insert candidate in DB
    candidate_id = insert_candidate(candidate)
    logger.info('Inserted candidate {} in DB'.format(candidate_id))
  except Exception as e:
    logger.error('Unable to insert candidate in DB: {}'.format(e))

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

      # Retrieve the entire active set
      A = list(active_set_collection.aggregate([
          {'$match': {}},
          {'$project': {'_id': 0, 'image_key': 1, 'usno_band': 1, 'panstarr_band': 1}}
        ]))

      # Define processes' chunk size
      num_processes = multiprocessing.cpu_count()
      chunk_size = math.floor(len(A)/num_processes)

      # Create `num_processes` parallel tasks
      tasks = [
        tcompute_v.s(
          json.dumps(candidate),
          A[(chunk_size * i):len(A) if i == num_processes - 1 else chunk_size * (i + 1)]
        ) for i in range(num_processes)
      ]

      # Define callback to execute when all parallel tasks are finished
      callback = thandle_compute_v_finished.s(json.dumps(candidate))

      # Execute chord in the background
      chord((tasks), callback).delay()
    else:
      logger.info('There are {} candidates stored in DB. Skipping...'.format(num_candidates))
  except Exception as e:
    logger.error('Unable to generate candidate: {}'.format(e))
