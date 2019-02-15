from cerberus import Validator
from ml_blink_api.config.celery_config import celery
from ml_blink_api.config.db import samples_collection
from ml_blink_api.models.sample import sample_schema
from ml_blink_api.utils.beta_samples import get_beta_csv_samples, parse_beta_sample

@celery.task
def insert_beta_samples_in_db():
  '''
  Insert valid beta samples in database
  '''
  if samples_collection.find().count() == 0:
    # Retrieve samples from .csv
    samples = get_beta_csv_samples()
    # Parse samples as defined in `sample_schema`
    parsed_samples = map(lambda x: parse_beta_sample(x), samples)
    # Filter samples by those that adhere to the `sample_schema` definition
    v = Validator(sample_schema)
    valid_samples = list(filter(lambda x: v.validate(x), parsed_samples))
    samples_collection.insert_many(valid_samples)
