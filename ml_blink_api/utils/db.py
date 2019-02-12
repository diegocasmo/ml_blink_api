import os
from pymongo import MongoClient

client = MongoClient(os.getenv('MONGO_URI') if os.getenv('ENV') == 'production' else 'db', 27017)
db = client[os.getenv('MONGO_DATABASE')]
