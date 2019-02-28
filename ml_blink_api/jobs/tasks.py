from cerberus import Validator
from ml_blink_api.config.celery_config import celery
from ml_blink_api.jobs.crawler import tgenerate_candidate

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
  # Executes every 60.0 seconds
  sender.add_periodic_task(60.0, tgenerate_candidate.s())
