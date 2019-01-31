from ml_blink_api.utils.db import db

# A schema which specifies the attributes of a user and their requirements
user_schema = {
  'email': {
    'type': 'string', 'minlength': 2, 'maxlength': 255, 'required': True,
    'empty': False, 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'
  },
  'password': {
    'type': 'string', 'minlength': 5, 'maxlength': 255, 'empty': False,
    'required': True
  },
  'salt': {'type': 'string'},
  'created_at': {'type': 'datetime', 'required': True, 'nullable': False},
  'updated_at': {'type': 'datetime', 'required': True, 'nullable': True}
}

def remove_auth_attrs(user):
  '''
  Remove user attributes related to authentication which must not be send to the client
  '''
  private_attrs = ['password', 'salt']
  for k in private_attrs:
    user.pop(k)
  return user

def get_test_user():
  '''
  A temporary test user, to whom all resources with a reference to a user belong to
  (matchings, comments, etc)
  '''
  return db.users.find_one({'email': 'darth.vader@it.uu.se'})
