from ml_blink_api.models.user import get_temp_test_user
from datetime import datetime

transformations_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'x': {'type': 'float', 'required': True, 'nullable': False},
    'y': {'type': 'float', 'required': True, 'nullable': False},
    'width': {'type': 'float', 'required': True, 'nullable': False},
    'height': {'type': 'float', 'required': True, 'nullable': False},
    'scale_x': {'type': 'float', 'default': 1, 'nullable': False},
    'scale_y': {'type': 'float', 'default': 1, 'nullable': False},
    'rotation': {'type': 'float', 'default': 0, 'nullable': False}
  }
}

image_schema = {
  'type': 'dict',
  'required': True,
  'schema': {
    'band': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
    'dataset': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
    'transformations': transformations_schema
  }
}

mission_schema = {
  'user_id': {'type': 'object_id', 'default_setter': lambda _ : get_temp_test_user().get('_id'), 'readonly': True},
  'image_key': {'type': 'integer', 'required': True, 'nullable': False},
  'accuracy_threshold': {'type': 'float', 'min': 0, 'max': 100, 'required': True, 'nullable': False},
  'accuracy': {'type': 'float', 'min': 0, 'max': 100, 'required': True, 'nullable': False},
  'image_one': image_schema,
  'image_two': image_schema,
  'created_at': {'type': 'integer', 'required': True, 'nullable': False}
}
