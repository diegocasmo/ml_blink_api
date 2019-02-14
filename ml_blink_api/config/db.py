import os
from pymongo import MongoClient

client = MongoClient(
  os.getenv('MONGO_URI') if os.getenv('FLASK_ENV') == 'production' else 'db', 27017,
  connect = False)
db = client[os.getenv('MONGO_DATABASE')]
