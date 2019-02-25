import numpy as np
from PIL import Image
from ml_blink_api.settings import APP_STATIC

def get_panstarr_vector(image_key, band):
  '''
  Return a PanSTARRs image specified by the `image_key` and `band` as a vector
  '''
  file_name = 'PanSTARR{}{}.jpg'.format(image_key, band)
  file_path = '{}/beta_images/PanSTARRS_ltd/{}'.format(APP_STATIC, file_name)
  return np.asarray(Image.open(file_path)).flatten()

def has_expected_panstarr_dim(image_key, band):
  '''
  Return true if the PanSTARRs image specified by an `image_key` and band has the expected
  dimensions, false otherwise
  '''
  panstarr_vector_size = 1200*1200
  return get_panstarr_vector(image_key, band).size == panstarr_vector_size
