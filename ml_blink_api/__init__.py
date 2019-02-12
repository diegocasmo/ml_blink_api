import os
from bson import ObjectId
from datetime import datetime
from json import JSONEncoder
from flask import Flask
from flask_cors import CORS
from ml_blink_api.resources.users.controllers import users
from ml_blink_api.resources.missions.controllers import missions
from ml_blink_api.resources.comments.controllers import comments
from ml_blink_api.resources.samples.controllers import samples
from cerberus import Validator, TypeDefinition

# Extend `cerberus` validator types with an ObjectId Type
Validator.types_mapping['object_id'] = TypeDefinition('object_id', (ObjectId,), ())

class CustomJSONEncoder(JSONEncoder):
  '''Extend the JSONEncoder class to handle MongoDB ObjectID and timestamps'''
  def default(self, obj):
    if isinstance(obj, ObjectId):
      return str(obj)
    if isinstance(obj, datetime):
      return obj.isoformat()
    return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.debug = int(os.getenv('DEBUG'))
app.secret_key = os.getenv('SECRET_KEY')
CORS(app, origins=os.getenv('ORIGINS').split(','))

app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(missions, url_prefix='/missions')
app.register_blueprint(comments, url_prefix='/comments')
app.register_blueprint(samples, url_prefix='/samples')
