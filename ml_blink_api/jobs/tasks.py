from cerberus import Validator
from pymongo import DESCENDING
from ml_blink_api.config.celery_config import celery
from ml_blink_api.config.db import db
from ml_blink_api.models.sample import sample_schema
from ml_blink_api.utils.beta_samples import get_beta_csv_samples, parse_beta_sample

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
  # Executes every 3600 seconds (1 hr)
  sender.add_periodic_task(3600.0, increment_counter.s(), name='increment counter')

@celery.task
def insert_beta_samples_in_db():
  '''
  Insert valid beta samples in database
  '''
  if db.samples.find().count() == 0:
    # Retrieve samples from .csv
    samples = get_beta_csv_samples()
    # Parse samples as defined in `sample_schema`
    parsed_samples = map(lambda x: parse_beta_sample(x), samples)
    # Filter samples by those that adhere to the `sample_schema` definition
    v = Validator(sample_schema)
    valid_samples = list(filter(lambda x: v.validate(x), parsed_samples))
    db.samples.insert_many(valid_samples)

@celery.task
def increment_counter():
  if db.counters.find().count() == 0:
    db.counters.insert_one({'count': 0})
  else:
    last_counter = db.counters.find_one({}, sort=[('_id', DESCENDING)])
    db.counters.insert_one({'count': last_counter.get('count') + 1})
