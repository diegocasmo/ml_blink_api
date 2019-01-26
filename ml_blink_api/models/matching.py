from bson import ObjectId

# A schema which specifies the attributes of a matching and their requirements
schema = {
  'accuracy': {
    'type': 'float',
    'required': True,
  },
  'user_id': {
    'type': 'string',
    'required': True,
  },
}

def serialize(matching):
  # Make sure all keys are JSON serializable
  for k in matching.keys():
    if isinstance(matching[k], ObjectId):
     matching[k] = str(matching[k])
  return matching
