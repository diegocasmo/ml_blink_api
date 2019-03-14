from ml_blink_api.config.celery_config import logger

def log_info(msg):
  '''
  Log a celery message as info
  '''
  logger.info(msg)

def log_error(msg):
  '''
  Log a celery message as an error
  '''
  logger.error(msg)
