import os
from ml_blink_api.config.db import users_collection

# A schema which specifies the attributes of a user and their requirements
user_schema = {
  'first_name': {
    'type': 'string', 'minlength': 2, 'maxlength': 255, 'required': True,
    'empty': False, 'nullable': False
  },
  'last_name': {
    'type': 'string', 'minlength': 2, 'maxlength': 255, 'required': True,
    'empty': False, 'nullable': False
  },
  'email': {
    'type': 'string', 'minlength': 2, 'maxlength': 255, 'required': True,
    'empty': False, 'nullable': False,
    'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'
  },
  'password': {
    'type': 'string', 'minlength': 5, 'maxlength': 255, 'empty': False,
    'required': True, 'nullable': False
  },
  'salt': {'type': 'string'},
  'created_at': {'type': 'number', 'required': True, 'nullable': False}
}

def remove_auth_attrs(user):
  '''
  Remove user attributes related to authentication which must not be send to the client
  '''
  private_attrs = ['password', 'salt']
  for k in private_attrs:
    user.pop(k)
  return user

def get_temp_test_user():
  '''
  A temporary test user, to whom all resources with a reference to a user belong to
  (missions, comments, etc)
  '''
  return users_collection.find_one({'email': os.getenv('TEMP_TEST_USER_EMAIL')})
