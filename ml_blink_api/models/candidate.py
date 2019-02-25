import time
from random import randint
from cerberus import Validator
from ml_blink_api.utils.usno import get_usno_vector, has_expected_usno_dim
from ml_blink_api.utils.panstarr import get_panstarr_vector, has_expected_panstarr_dim
from ml_blink_api.utils.dataset_bands import datasets_bands
from ml_blink_api.config.db import candidates_collection

# A schema which specifies the attributes of a candidate and their requirements
candidate_schema = {
  'image_key': {'type': 'integer', 'required': True, 'nullable': False},
  'usno_band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
  'panstarr_band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
  'created_at': {'type': 'number', 'required': True, 'nullable': False}
}

def generate_random_candidate():
  '''
  Generate a pseudo-random candidate by selecting a random `image_key` and dataset bands for USNO and PanSTARRS
  '''
  attrs = None
  min_image_key = 0
  max_image_key = 1000
  has_expected_dimensions = False
  while not has_expected_dimensions:
    # Randomly generate a candidate
    attrs = {
      'image_key': randint(min_image_key, max_image_key),
      'usno_band': datasets_bands[randint(0, len(datasets_bands) - 1)].get('USNO', 'blue1'),
      'panstarr_band': datasets_bands[randint(0, len(datasets_bands) - 1)].get('PanSTARR', 'g'),
      'created_at': int(round(time.time() * 1000))
    }

    # Verify candidate has expected dimensions
    has_expected_dimensions = has_expected_dim(attrs)

  # Return candidate of expected dimensions
  return attrs

def has_expected_dim(attrs):
  '''
  Return true if candidate's attributes have expected dimensions, false otherwise
  '''
  return has_expected_usno_dim(attrs.get('image_key'), attrs.get('usno_band')) and \
    has_expected_panstarr_dim(attrs.get('image_key'), attrs.get('panstarr_band'))

def insert_candidate(v, attrs):
  '''
  Attempt to insert a candidate in DB. Return candidate id if successful, throw an exception
  with an array of errors otherwise
  '''
  # Verify if candidate should be stored
  theta = 0.5
  if v >= theta: raise ValueError('v = {}, but it must be v < {}. Skipping potential candidate...'.format(v, theta))

  # Candidate should be inserted if valid
  validator = Validator(candidate_schema)
  if validator.validate(attrs):
    return candidates_collection.insert_one(validator.document).inserted_id
  else:
    raise ValueError(validator.errors)
