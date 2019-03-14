from random import randint
from cerberus import Validator
from ml_blink_api.utils.usno import has_expected_usno_dim
from ml_blink_api.utils.panstarr import has_expected_panstarr_dim
from ml_blink_api.utils.dataset_bands import datasets_bands
from ml_blink_api.config.db import candidates_collection

# A schema which specifies the attributes of a candidate and their requirements
candidate_schema = {
  'image_key': {'type': 'integer', 'required': True, 'nullable': False},
  'usno_band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
  'panstarr_band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
  'v': {'type': 'float', 'required': True, 'nullable': False}
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
      'panstarr_band': datasets_bands[randint(0, len(datasets_bands) - 1)].get('PanSTARR', 'g')
    }

    # Verify candidate has expected dimensions
    has_expected_dimensions = has_expected_dim(attrs)

  # Return candidate of expected dimensions
  return attrs

def has_expected_dim(candidate):
  '''
  Return true if candidate's attributes have expected dimensions, false otherwise
  '''
  return has_expected_usno_dim(candidate.get('image_key'), candidate.get('usno_band')) and \
    has_expected_panstarr_dim(candidate.get('image_key'), candidate.get('panstarr_band'))

def insert_candidate(attrs):
  '''
  Return candidate id of the inserted candidate in DB if successful, throw an exception
  with an array of errors otherwise
  '''
  if not has_expected_dim(attrs): raise ValueError('Candidate {} has invalid dimensions'.format(attrs))

  v = Validator(candidate_schema)
  if v.validate(attrs):
    return candidates_collection.insert_one(v.document).inserted_id
  else:
    raise ValueError(v.errors)
