import numpy as np
from PIL import Image
from ml_blink_api.settings import APP_STATIC
from ml_blink_api.utils.linalg import normalize

PANSTARR_VECTOR_SIZE = 1200*1200

def get_panstarr_vector(image_key, band):
  '''
  Return a PanSTARRs image specified by the `image_key` and `band` as a vector
  '''
  file_name = 'PanSTARR{}{}.jpg'.format(image_key, band)
  file_path = '{}/beta_images/PanSTARRS_ltd/{}'.format(APP_STATIC, file_name)
  return np.asarray(Image.open(file_path)).flatten()

def get_panstarr_projection(image_key, band, num_proj = 10000):
  '''
  Return a normalized PanSTARRs vector with its dimensionality reduced to `num_proj`
  '''
  xs = get_panstarr_vector(image_key, band)
  slices = np.arange(0, PANSTARR_VECTOR_SIZE, int(PANSTARR_VECTOR_SIZE / num_proj))
  return normalize(np.add.reduceat(xs, slices))

def has_expected_panstarr_dim(image_key, band):
  '''
  Return true if the PanSTARRs image specified by an `image_key` and band has the expected
  dimensions, false otherwise
  '''
  return get_panstarr_vector(image_key, band).size == PANSTARR_VECTOR_SIZE
