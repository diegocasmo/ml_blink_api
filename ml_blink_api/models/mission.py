from ml_blink_api.models.user import get_temp_test_user
from datetime import datetime

transformations_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'x': {'type': 'float', 'coerce': float, 'required': True, 'nullable': False},
    'y': {'type': 'float', 'coerce': float, 'required': True, 'nullable': False},
    'width': {'type': 'float', 'coerce': float, 'required': True, 'nullable': False},
    'height': {'type': 'float', 'coerce': float, 'required': True, 'nullable': False},
    'scale_x': {'type': 'float', 'coerce': float, 'default': 1, 'nullable': False},
    'scale_y': {'type': 'float', 'coerce': float, 'default': 1, 'nullable': False},
    'rotation': {'type': 'float', 'coerce': float, 'default': 0, 'nullable': False}
  }
}

image_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'key': {'type': 'integer', 'coerce': int, 'required': True, 'nullable': False},
    'band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
    'dataset': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
    'transformations': transformations_schema
  }
}


mission_schema = {
  'user_id': {'type': 'string', 'default_setter': lambda _ : str(get_temp_test_user().get('_id')), 'readonly': True},
  'accuracy': {'type': 'float', 'coerce': float, 'min': 0, 'max': 100, 'required': True, 'nullable': False},
  'solved': {'type': 'boolean', 'coerce': bool, 'required': True, 'nullable': False},
  'image_one': image_schema,
  'image_two': image_schema,
  'created_at': {'type': 'datetime', 'default_setter': lambda _ : datetime.now(), 'readonly': True}
}
