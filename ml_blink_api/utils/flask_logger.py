from flask import current_app

def log_info(msg):
  '''
  Log a message as info
  '''
  current_app.logger.info(msg)

def log_error(msg):
  '''
  Log a message as an error
  '''
  current_app.logger.error(msg)
