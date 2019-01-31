# A schema which specifies the attributes of a matching and their requirements
schema = {
  'accuracy': {
    'type': 'float',
    'coerce': float,
    'required': True,
  },
  'user_id': {
    'type': 'string',
    'required': True,
  },
}
