"""Load every bundled school record into MongoDB.

Run this after changing the JSON files:
    python import_data.py

The operation is idempotent: records are upserted by their stable ID, so it
also repairs a partly imported collection without creating duplicates.
"""

import json
from pathlib import Path

from mongo_service import db


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATASETS = (
    ("students_recovered.json", "students", "student_id"),
    ("parents_recovered.json", "parents", "parent_id"),
    ("teachers.json", "teachers", "teacher_id"),
    ("principals_recovered.json", "principals", "principal_id"),
)


def load_records(filename: str) -> list[dict]:
    with (DATA_DIR / filename).open(encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON list")
    return records


def import_collection(filename: str, collection_name: str, id_field: str) -> int:
    records = load_records(filename)
    collection = db[collection_name]

    collection.create_index(id_field, unique=True)
    for record in records:
        record_id = record.get(id_field)
        if not record_id:
            raise ValueError(f"{filename} has a record without {id_field}")
        collection.replace_one({id_field: record_id}, record, upsert=True)

    imported_ids = {record[id_field] for record in records}
    stored_ids = set(collection.distinct(id_field))
    missing_ids = imported_ids - stored_ids
    if missing_ids:
        raise RuntimeError(
            f"{collection_name}: failed to store {sorted(missing_ids)}"
        )

    print(f"{collection_name}: {len(imported_ids)} records verified")
    return len(imported_ids)


def import_all_data() -> dict[str, int]:
    counts = {
        collection_name: import_collection(filename, collection_name, id_field)
        for filename, collection_name, id_field in DATASETS
    }
    print("All APTRA data imported and verified successfully.")
    return counts


if __name__ == "__main__":
    import_all_data()
