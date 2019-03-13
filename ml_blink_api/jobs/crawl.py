import numpy as np
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.models.candidate import insert_candidate
from ml_blink_api.utils.dataset_bands import datasets_bands
from ml_blink_api.config.celery_config import celery, logger
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.config.db import active_set_collection, anomalies_collection, candidates_collection

def get_potential_candidates(m, dataset_bands):
  '''
  Generate candidates for each element in m. Note this only uses the 'blue1' (USNO)
  and 'g' (PanSTARR) bands since the fake generated images are all equal across all
  the bands
  '''
  potential_candidates = [
    {
      'image_key': i,
      'usno_band': datasets_bands[0].get('USNO'),
      'panstarr_band': datasets_bands[0].get('PanSTARR')
    }
    for i in range(m)
  ]

  # Retrieve active set, current candidates, and known anomalies to avoid crawling them again
  attrs_proj = {'_id': 0, 'image_key': 1, 'usno_band': 1, 'panstarr_band': 1}
  active_set = active_set_collection.aggregate([{'$match': {}}, {'$project': attrs_proj}])
  candidates = candidates_collection.aggregate([{'$match': {}}, {'$project': attrs_proj}])
  anomalies = anomalies_collection.aggregate([{'$match': {}}, {'$project': attrs_proj}])

  known_candidates = list(active_set) + list(candidates) + list(anomalies)
  return list(filter(lambda x: x not in known_candidates, potential_candidates))

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

    # Get active set
    A = list(active_set_collection.find())

    # Compute `v` for each element in S
    vs = {}
    for s in S:
      try:
        # Each `v` is initially set to 0
        vs[s.get('image_key')] = 0

        # Compute `v` using the members of the active set
        x = get_usno_projection(s.get('image_key'), s.get('usno_band'))
        y = get_panstarr_projection(s.get('image_key'), s.get('panstarr_band'))
        for i in range(len(A)):
          xi = A[i].get('usno_vector')
          yi = A[i].get('panstarr_vector')
          v = np.dot(np.dot(x, xi), np.dot(y, yi))
          # Keep track of each v value
          vs[s.get('image_key')] = vs[s.get('image_key')] + v if s.get('image_key') in vs else v
      except Exception as e:
        logger.error('Exception thrown: {}'.format(e))
        # An exception might be thrown if an image file doesn't exist. If so, assume candidate is
        # infinitely unlikely to be an anomaly
        vs[s.get('image_key')] = float('Inf')

    # Find minimum `v` value and index (`image_key`)
    vm = min(vs.values())
    vi = [k for k in vs if vs[k] == vm][0]

    # Extend candidate with its `v` value
    attrs = list(filter(lambda x: x.get('image_key') == vi, S))[0]
    attrs['v'] = vm
    candidate_id = insert_candidate(attrs)
    logger.info('[vi vm id]: [{} {} {}]'.format(vi, vm, candidate_id))
  except Exception as e:
    logger.error('Unable to crawl candidates: {}'.format(e))
