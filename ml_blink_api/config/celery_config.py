import os
from celery import Celery
from celery.utils.log import get_task_logger

celery = Celery('tasks',
  broker = os.getenv('CELERY_BROKER_URL'),
  backend = os.getenv('CELERY_RESULT_BACKEND'))

logger = get_task_logger(__name__)

if __name__ == '__main__':
  celery.start()
