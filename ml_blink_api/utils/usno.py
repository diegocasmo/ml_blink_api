import numpy as np
from PIL import Image
from ml_blink_api.settings import APP_STATIC

def get_usno_vector(image_key, band):
  '''
  Return an USNO image specified by the `image_key` and `band` as a vector
  '''
  file_name = 'USNO{}{}.gif'.format(image_key, band)
  file_path = '{}/beta_images/USNO1001/{}'.format(APP_STATIC, file_name)
  xs = np.asarray(Image.open(file_path)).flatten()
  return xs/np.linalg.norm(xs, 2)

def has_expected_usno_dim(image_key, band):
  '''
  Return true if the USNO image specified by an `image_key` and band has the expected
  dimensions, false otherwise
  '''
  usno_vector_size = 297*298
  return get_usno_vector(image_key, band).size == usno_vector_size
