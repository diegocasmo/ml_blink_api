import os
from bson import ObjectId
from datetime import datetime
from json import JSONEncoder
from flask import Flask
from flask_cors import CORS
from ml_blink_api.resources.users.controllers import users
from ml_blink_api.resources.missions.controllers import missions
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
CORS(app, origins=os.getenv('ORIGINS'))

app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(missions, url_prefix='/missions')
