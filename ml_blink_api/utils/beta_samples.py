import os
import csv
import time
from itertools import islice
from cerberus import Validator
from ml_blink_api.utils.db import db
from ml_blink_api.models.sample import sample_schema

def insert_beta_samples_in_db():
  '''
  Insert valid beta samples in database
  '''
  print('Inserting beta samples in DB...')
  # Retrieve samples from .csv
  samples = get_beta_csv_samples()
  # Parse samples as defined in `sample_schema`
  parsed_samples = map(lambda x: parse_beta_sample(x), samples)
  # Filter samples by those that adhere to the `sample_schema` definition
  v = Validator(sample_schema)
  valid_samples = list(filter(lambda x: v.validate(x), parsed_samples))
  inserted_ids = db.samples.insert_many(valid_samples).inserted_ids
  print("Inserted {} out of {} beta samples".format(len(inserted_ids), len(samples)))

def get_beta_csv_samples(file_name = 'beta.csv'):
  '''
  Return all samples defined in the beta .csv file
  '''
  file_path = "{}/data/{}".format(os.getcwd(), file_name)
  samples = []
  with open(file_path) as csv_file:
    rows = csv.reader(csv_file, delimiter=',')
    start_row = 1 # Avoid reading header row
    samples = [x for x in islice(rows, start_row, None)]
  return samples

def parse_beta_sample(sample):
  '''
  Parse a sample from the beta .csv file to a sample as defined in `sample_schema`
  '''
  as_float = lambda x: None if x == '?' else float(x)
  as_int = lambda x: None if x == '?' else int(x)
  image_key = as_int(sample[13])
  usno_images_dir = "{}/static/beta_images/USNO1001".format(os.getcwd())
  panstarr_images_dir = "{}/static/beta_images/PanSTARRS_ltd".format(os.getcwd())
  return {
    'usno_b1_id': sample[1],
    'usno_ra': as_float(sample[2]),
    'usno_dec': as_float(sample[3]),
    'panstarr_ra': as_float(sample[4]),
    'panstarr_dec': as_float(sample[5]),
    'red1_mag': as_float(sample[6]),
    'red2_mag': as_float(sample[7]),
    'blue1_mag': as_float(sample[8]),
    'blue2_mag': as_float(sample[9]),
    'pm_ra': as_float(sample[10]),
    'pm_dec': as_float(sample[11]),
    'diff': as_float(sample[12]),
    'image_key': image_key,
    'usno_blue1_image_path': "{}/USNO{}blue1.gif".format(usno_images_dir, image_key),
    'usno_blue2_image_path': "{}/USNO{}blue2.gif".format(usno_images_dir, image_key),
    'usno_red1_image_path': "{}/USNO{}red1.gif".format(usno_images_dir, image_key),
    'usno_red2_image_path': "{}/USNO{}red2.gif".format(usno_images_dir, image_key),
    'usno_ir_image_path': "{}/USNO{}ir.gif".format(usno_images_dir, image_key),
    'panstarr_g_image_path': "{}/PanSTARR{}g.jpg".format(panstarr_images_dir, image_key),
    'panstarr_r_image_path': "{}/PanSTARR{}r.jpg".format(panstarr_images_dir, image_key),
    'panstarr_z_image_path': "{}/PanSTARR{}z.jpg".format(panstarr_images_dir, image_key),
    'created_at': int(round(time.time() * 1000))
  }
