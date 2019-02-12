# A sample represents an instance of an object used for training

# A schema which specifies the attributes of a sample and their requirements
sample_schema = {
  'usno_b1_id': {'type': 'string', 'required': True, 'nullable': False},
  'usno_ra': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'usno_dec': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'panstarr_ra': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'panstarr_dec': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'red1_mag': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'red2_mag': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'blue1_mag': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'blue2_mag': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'pm_ra': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'pm_dec': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'diff': {'type': 'number', 'required': True, 'default': None, 'nullable': True},
  'image_key': {'type': 'integer', 'required': True, 'nullable': False},
  'usno_blue1_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'usno_blue2_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'usno_red1_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'usno_red2_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'usno_ir_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'panstarr_g_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'panstarr_r_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'panstarr_z_image_path': {'type': 'string', 'required': True, 'nullable': False},
  'created_at': {'type': 'number', 'required': True, 'nullable': False}
}
