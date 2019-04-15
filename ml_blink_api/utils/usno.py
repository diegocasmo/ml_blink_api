import numpy as np
from PIL import Image
from ml_blink_api.settings import APP_STATIC
from ml_blink_api.utils.linalg import normalize

USNO_VECTOR_SIZE = 297*298

def get_usno_vector(image_key, band):
  '''
  Return an USNO image specified by the `image_key` and `band` as a vector
  '''
  file_name = 'USNO{}{}.gif'.format(image_key, band)
  file_path = '{}/beta_images/USNO1001/{}'.format(APP_STATIC, file_name)
  return np.asarray(Image.open(file_path)).flatten()

def get_usno_projection(image_key, band, num_proj = 4000):
  '''
  Return a normalized USNO vector with its dimensionality reduced to `num_proj`
  '''
  xs = get_usno_vector(image_key, band)
  slices = np.arange(0, USNO_VECTOR_SIZE, int(USNO_VECTOR_SIZE / num_proj))
  return normalize(np.add.reduceat(xs, slices))

def has_expected_usno_dim(image_key, band):
  '''
  Return true if the USNO image specified by an `image_key` and band has the expected
  dimensions, false otherwise
  '''
  return get_usno_vector(image_key, band).size == USNO_VECTOR_SIZE
