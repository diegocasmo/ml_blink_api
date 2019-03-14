import operator
import numpy as np
from functools import reduce
from ml_blink_api.config.celery_config import celery
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.models.candidate import insert_candidate
from ml_blink_api.utils.dataset_bands import datasets_bands
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.utils.celery_logger import log_info, log_error
from ml_blink_api.config.db import active_set_collection, anomalies_collection, candidates_collection

def get_potential_candidates(m, bands):
  '''
  Generate candidates for each element in m. Note this only uses the 'blue1' (USNO)
  and 'g' (PanSTARR) bands since the fake generated images are all equal across all
  the bands
  '''
  potential_candidates = reduce(operator.concat, [
    [
      {
        'image_key': i,
        'usno_band': bands[j].get('USNO'),
        'panstarr_band': bands[j].get('PanSTARR')
      }
      for j in range(len(bands))
    ]
    for i in range(m)
  ])

  # Retrieve known anomalies to avoid crawling them again
  anomalies = list(anomalies_collection.aggregate([
    {'$match': {}},
    {'$project': {'_id': 0, 'image_key': 1, 'usno_band': 1, 'panstarr_band': 1}}]
  ))
  return list(filter(lambda x: x not in anomalies, potential_candidates))

def get_s_id(s):
  '''
  Return a string which uniquely identifies an element of `S`
  '''
  return '{}.{}.{}'.format(s.get('image_key'), s.get('usno_band'), s.get('panstarr_band'))

def compute_v(S):
  '''
  Return a dictionary where keys represent `S` candidates encoded using their `s_id` and
  values their respective `v`
  '''
  # Retrieve active set
  A = list(active_set_collection.aggregate([
    {'$match': {}},
    {'$project': {'_id': 0, 'usno_vector': 1, 'panstarr_vector': 1}}
  ]))

  # Compute `v` for each element in `S`
  vs = {}
  for s in S:
    try:
      # Each `v` is initially set to 0
      s_id = get_s_id(s)
      vs[s_id] = 0

      # Retrieve potential candidate's projections
      x = get_usno_projection(s.get('image_key'), s.get('usno_band'))
      y = get_panstarr_projection(s.get('image_key'), s.get('panstarr_band'))

      # Compute `v` using the members of the active set
      for member in A:
        xi = member.get('usno_vector')
        yi = member.get('panstarr_vector')
        v = np.dot(np.dot(x, xi), np.dot(y, yi))

        # Keep track of each `v` value using `s_id`
        vs[s_id] = vs[s_id] + v if s_id in vs else v
    except Exception as e:
      log_error('Exception thrown: {}'.format(e))
      # An exception might be thrown if an image file doesn't exist. If so, assume candidate is
      # infinitely unlikely to be an anomaly
      vs[s_id] = float('Inf')
  return vs

@celery.task(name='tcrawl_candidates')
def tcrawl_candidates():
  '''
  Crawl potential candidates in `m` and add the one with the lowest `v` value to the
  candidates collection
  '''
  try:
    # Generate candidates that will be crawled
    m = 1001
    S = get_potential_candidates(m, datasets_bands)

    # Compute the `v` value for each potential candidate in `S`
    vs = compute_v(S)

    # Find minimum `v` value and `s_id`
    vm = min(vs.values())
    vm_s_id = next(s_id for s_id in vs if vs[s_id] == vm)

    # Extend candidate with its `v` value
    attrs = next(s for s in S if get_s_id(s) == vm_s_id)
    attrs['v'] = vm
    candidate_id = insert_candidate(attrs)
    log_info('[vm_s_id vm id]: [{} {} {}]'.format(vm_s_id, vm, candidate_id))
  except Exception as e:
    log_error('Unable to crawl candidates: {}'.format(e))
