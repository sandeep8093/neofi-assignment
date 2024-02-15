from pymongo import MongoClient

from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(dotenv_path)

class ConnectDB:
    def __init__(self):
        self.connection = None
        self.collection = None

    def connect_db(self, db='', collection=''):   # Fetches the MongoDB, by making use of Request Body
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable not set")

        connection = MongoClient(mongodb_uri)
        return connection
