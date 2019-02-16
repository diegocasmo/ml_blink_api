import os
from celery import Celery

celery = Celery('tasks',
  broker = os.getenv('CELERY_BROKER_URL'),
  backend = os.getenv('CELERY_RESULT_BACKEND'))

if __name__ == '__main__':
  celery.start()
