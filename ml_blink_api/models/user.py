from bson import ObjectId

# A schema which specifies the attributes of a user and their requirements
schema = {
  'email': {
    'type': 'string',
    'minlength': 2,
    'maxlength': 255,
    'required': True,
    'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$'
  },
  'password': {
    'type': 'string',
    'minlength': 5,
    'maxlength': 255,
    'required': True,
  },
  'salt': {
    'type': 'string',
  },
}

def serialize(user):
  # Remove keys of the user object which are private and shouldn't be sent to the client
  private_keys = ['password', 'salt']
  for k in private_keys:
    user.pop(k)

  # Make sure all keys are JSON serializable
  for k in user.keys():
    if isinstance(user[k], ObjectId):
     user[k] = str(user[k])
  return user
