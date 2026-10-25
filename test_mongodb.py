import os
import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()
uri = os.getenv("MONGO_DB_URL")

if not uri:
    raise ValueError(
        "MONGO_DB_URL environment variable is not set. Please set it in your .env file or environment."
    )

# Create a new client and connect to the server with certifi CA bundle
client = MongoClient(uri, tlsCAFile=certifi.where())

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")