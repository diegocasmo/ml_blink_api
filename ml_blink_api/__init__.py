import os
from bson import ObjectId
from datetime import datetime
from json import JSONEncoder
from flask import Flask
from flask_cors import CORS
from cerberus import Validator, TypeDefinition
from ml_blink_api.resources.crawl.controllers import crawl
from ml_blink_api.resources.users.controllers import users
from ml_blink_api.resources.missions.controllers import missions
from ml_blink_api.resources.comments.controllers import comments
from ml_blink_api.resources.candidates.controllers import candidates
from ml_blink_api.resources.potential_anomalies.controllers import potential_anomalies

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

# Configure the Flask application
app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.debug = int(os.getenv('DEBUG'))
app.secret_key = os.getenv('SECRET_KEY')
CORS(app, origins=os.getenv('ORIGINS').split(','))

# Register API endpoints using blueprint
app.register_blueprint(crawl, url_prefix='/crawl')
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(missions, url_prefix='/missions')
app.register_blueprint(comments, url_prefix='/comments')
app.register_blueprint(candidates, url_prefix='/candidates')
app.register_blueprint(potential_anomalies, url_prefix='/potential_anomalies')
