import math
import json
import random
import operator
import numpy as np
import multiprocessing
from celery import chord
from functools import reduce
from pymongo import DESCENDING
from ml_blink_api.config.celery_config import celery
from ml_blink_api.utils.usno import get_usno_projection
from ml_blink_api.models.candidate import insert_candidate
from ml_blink_api.utils.dataset_bands import datasets_bands
from ml_blink_api.utils.panstarr import get_panstarr_projection
from ml_blink_api.utils.celery_logger import log_info, log_error
from ml_blink_api.config.db import db

MAX_TIME_STEPS = 1500
# NUM_PROJ = [10, 20, 50, 100, 200, 500, 1000, 2500, 5000, 7500, 10000]
NUM_PROJ = [1001]

ANOMALIES = [{
  'image_key': 13,
  'usno_band': 'blue2',
  'panstarr_band': 'g'
}, {
  'image_key': 56,
  'usno_band': 'blue2',
  'panstarr_band': 'g'
}, {
  'image_key': 679,
  'usno_band': 'blue2',
  'panstarr_band': 'g'
}, {
  'image_key': 831,
  'usno_band': 'blue2',
  'panstarr_band': 'g'
}]

def get_potential_candidates(image_keys, bands, num_proj):
  '''
  Generate potential candidates for each image key, ignoring those that have
  already been tagged as anomalies
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
    for i in image_keys
  ])

  # Retrieve known anomalies to avoid crawling them again
  anomalies = list(db['anomalies_{}'.format(num_proj)].aggregate([
    {'$match': {}},
    {'$project': {'_id': 0, 'image_key': 1, 'usno_band': 1, 'panstarr_band': 1}}
  ]))
  return list(filter(lambda x: x not in anomalies, potential_candidates))

def get_s_id(s):
  '''
  Return a string which uniquely identifies an element of `S`
  '''
  return '{}.{}.{}'.format(s.get('image_key'), s.get('usno_band'), s.get('panstarr_band'))

def increment_time_step(num_proj):
  '''
  Increment steps + 1
  '''
  if db['time_steps_{}'.format(num_proj)].find().count() == 0:
    db['time_steps_{}'.format(num_proj)].insert_one({'count': 0})
  else:
    last_time_step = db['time_steps_{}'.format(num_proj)].find_one({}, sort=[('_id', DESCENDING)])
    db['time_steps_{}'.format(num_proj)].insert_one({'count': last_time_step.get('count') + 1})

@celery.task(name='ml_blink_101_tcompute_v')
def ml_blink_101_tcompute_v(S, num_proj):
  '''
  Return a dictionary where keys represent `S` candidates encoded using their `s_id` and
  values their respective `v`
  '''
  # Retrieve potential candidates in `S`
  S = json.loads(S)

  # Retrieve active set
  A = list(db['active_set_{}'.format(num_proj)].aggregate([
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
      x = get_usno_projection(s.get('image_key'), s.get('usno_band'), num_proj)
      y = get_panstarr_projection(s.get('image_key'), s.get('panstarr_band'), num_proj)

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

@celery.task(name='ml_blink_101_thandle_compute_v_finished')
def ml_blink_101_thandle_compute_v_finished(results, S, num_proj):
  '''
  Create a candidate in DB given the result of each individual process computation
  '''
  try:
    # Retrieve processes' results and `S`
    S = json.loads(S)
    vs = reduce(lambda acc, x: acc.update(x) or acc, results, {})

    # Find minimum `v` value and `s_id`
    vm = min(vs.values())
    vm_s_id = [s_id for s_id in vs if vs[s_id] == vm]
    # Break ties randomly
    if len(vm_s_id) > 1:
      vm_s_id = random.choice(vm_s_id)
    else:
      vm_s_id = vm_s_id[0]

    # Remove anomaly from S if found, add to the active set otherwise
    attrs = next(s for s in S if get_s_id(s) == vm_s_id)
    if attrs in ANOMALIES:
      anomaly_id = db['anomalies_{}'.format(num_proj)].insert_one(attrs).inserted_id
      log_info('Inserted anomaly with id {} in the anomalies collection'.format(anomaly_id))
    else:
      # Extend candidate with its `v` value
      attrs['v'] = vm
      attrs['usno_vector'] = get_usno_projection(attrs.get('image_key'), attrs.get('usno_band'), num_proj).tolist()
      attrs['panstarr_vector'] = get_panstarr_projection(attrs.get('image_key'), attrs.get('panstarr_band'), num_proj).tolist()
      member_id = db['active_set_{}'.format(num_proj)].insert_one(attrs).inserted_id
      log_info('Inserted member with id {} in active set'.format(member_id))

    # Keep crawling until we have reached the max number of time-steps
    last_time_step = db['time_steps_{}'.format(num_proj)].find_one({}, sort=[('_id', DESCENDING)])
    if last_time_step.get('count') < MAX_TIME_STEPS:
      ml_blink_101_tcrawl_candidates.delay(num_proj)
    else:
      next_proj_index = NUM_PROJ.index(num_proj) + 1
      if next_proj_index < len(NUM_PROJ):
        ml_blink_101_tcrawl_candidates.delay(NUM_PROJ[next_proj_index])

  except Exception as e:
    log_error('Unable to insert candidate in DB: {}'.format(e))

@celery.task(name='ml_blink_101_tcrawl_candidates')
def ml_blink_101_tcrawl_candidates(num_proj = None):
  '''
  Crawl potential candidates in `m` and add the one with the lowest `v` value to the
  candidates collection
  '''
  try:
    num_proj = num_proj or NUM_PROJ[0]
    # Update current time step
    increment_time_step(num_proj)

    # Generate candidates that will be crawled
    m = 1001
    S = get_potential_candidates(range(m), datasets_bands, num_proj)

    log_info('Crawling {} potential candidates'.format(len(S)))

    # Define processes' chunk size
    num_processes = multiprocessing.cpu_count()
    chunk_size = math.floor(len(S)/num_processes)

    # Create `num_processes` parallel tasks
    tasks = [
      ml_blink_101_tcompute_v.s(
        json.dumps(
          S[(chunk_size * i):(len(S) if i == num_processes - 1 else chunk_size * (i + 1))],
        ),
        num_proj
      ) for i in range(num_processes)
    ]

    # Define callback to execute when all parallel tasks are finished
    callback = ml_blink_101_thandle_compute_v_finished.s(json.dumps(S), num_proj)

    # Execute chord in the background
    chord((tasks), callback).delay()
  except Exception as e:
    log_error('Unable to crawl candidates: {}'.format(e))
