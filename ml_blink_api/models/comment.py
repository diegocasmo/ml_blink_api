from ml_blink_api.models.user import get_temp_test_user
from datetime import datetime

comment_schema = {
  'user_id': {'type': 'object_id', 'default_setter': lambda _ : get_temp_test_user().get('_id'), 'readonly': True},
  'image_key': {'type': 'integer', 'required': True, 'nullable': False},
  'text': {'type': 'string', 'required': True, 'empty': False, 'nullable': False},
  'created_at': {'type': 'datetime', 'default_setter': lambda _ : datetime.now(), 'readonly': True}
}
