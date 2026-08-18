from mongo_service import db
from mock_api import load_json

def import_collection(filename, collection_name):
    data = load_json(filename)

    collection = db[collection_name]

    # Clear existing data in this APTRA collection
    collection.delete_many({})

    if data:
        collection.insert_many(data)

    print(f"{collection_name}: {len(data)} records imported")


import_collection("students.json", "students")
import_collection("parents.json", "parents")
import_collection("teachers.json", "teachers")
import_collection("principal.json", "principals")

print("All APTRA data imported successfully.")