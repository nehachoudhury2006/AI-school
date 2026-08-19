import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Support the existing project setting as well as the correctly spelled name.
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MNGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "APTRA_AI")

client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]


def test_connection():
    client.admin.command("ping")
    return True
