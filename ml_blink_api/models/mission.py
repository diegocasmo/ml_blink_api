transformations_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'rotation': {'type': 'float', 'coerce': float, 'required': True},
    'width': {'type': 'float', 'coerce': float, 'required': True},
    'height': {'type': 'float', 'coerce': float, 'required': True},
    'x': {'type': 'float', 'coerce': float, 'required': True},
    'y': {'type': 'float', 'coerce': float, 'required': True}
  }
}

image_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'key': {'type': 'integer', 'coerce': int, 'required': True},
    'band': {'type': 'string', 'required': True, 'empty': False},
    'dataset': {'type': 'string', 'required': True, 'empty': False},
    'transformations': transformations_schema
  }
}

mission_schema = {
  'user_id': {'type': 'string', 'required': True, 'empty': False},
  'accuracy': {'type': 'float', 'coerce': float, 'min': 0, 'max': 100, 'required': True},
  'solved': {'type': 'boolean', 'coerce': bool, 'required': True},
  'image_one': image_schema,
  'image_two': image_schema,
  'created_at': {'type': 'datetime', 'required': True, 'nullable': False},
  'updated_at': {'type': 'datetime', 'required': True, 'nullable': True}
}
