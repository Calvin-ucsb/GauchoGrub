import os
from pymongo import MongoClient

client = None
db = None

def init_mongo():
    global client, db
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB", "gauchogrub")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db
