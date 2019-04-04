import os
from pymongo import MongoClient

client = MongoClient(
  os.getenv('MONGO_URI') if os.getenv('FLASK_ENV') == 'production' else 'db', 27017,
  connect = False)

db = client[os.getenv('MONGO_DATABASE')]

# Store a reference to each MongoDB collection
comments_collection = db.comments
missions_collection = db.missions
users_collection = db.users
candidates_collection = db.candidates
active_set_collection = db.active_set
potential_anomalies_collection = db.potential_anomalies
