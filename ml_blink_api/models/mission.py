from ml_blink_api.models.user import get_temp_test_user

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
  'accuracy': {'type': 'float', 'min': 0, 'max': 100, 'required': True, 'nullable': False},
  'is_accuracy_valid': {'type': 'boolean', 'required': True, 'empty': False, 'nullable': False},
  'accuracy_threshold': {'type': 'float', 'min': 0, 'max': 100, 'required': True, 'nullable': False},
  'image_one': image_schema,
  'image_two': image_schema,
  'created_at': {'type': 'number', 'required': True, 'nullable': False}
}

def matching_has_overlap(mission):
  '''
  Return true if a mission's matching images overlap (one is placed on top of the
  other), false otherwise
  '''
  img_1 = mission.get('image_one').get('transformations')
  img_2 = mission.get('image_two').get('transformations')

  # Retrieve images' coordinates
  x1 = img_1.get('x')
  y1 = img_1.get('y')
  x2 = img_2.get('x')
  y2 = img_2.get('y')

  # Compute `x` and `y` coordinate end points for each image
  x1_end = x1 + (img_1.get('width') * img_1.get('scale_x'))
  y1_end = y1 + (img_1.get('height') * img_1.get('scale_y'))
  x2_end = x2 + (img_2.get('width') * img_2.get('scale_x'))
  y2_end = y2 + (img_2.get('height') * img_2.get('scale_y'))

  # Verify if there's overlap in each coordinate
  x_overlap = (x1 <= x2 and x2 <= x1_end) or (x2 < x1 and x2_end >= x1)
  y_overlap = (y1 <= y2 and y2 <= y1_end) or (y2 < y1 and y2_end >= y1)

  return x_overlap and y_overlap
