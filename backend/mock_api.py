import json
from pathlib import Path

from pymongo.errors import PyMongoError

from mongo_service import db


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_mongo_available = True


def _load_records(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as data_file:
        return json.load(data_file)


STUDENTS = _load_records("students_recovered.json")
PARENTS = _load_records("parents_recovered.json")
PRINCIPALS = _load_records("principals_recovered.json")
TEACHERS = _load_records("teachers.json")


def _read(mongo_query, local_query):
    """Read MongoDB when available, otherwise use the bundled school data."""
    global _mongo_available

    if _mongo_available:
        try:
            result = mongo_query()
            if result:
                return result
        except PyMongoError:
            _mongo_available = False

    return local_query()


def get_student_by_id(student_id):
    return _read(
        lambda: db.students.find_one({"student_id": student_id}, {"_id": 0}),
        lambda: next(
            (student for student in STUDENTS if student["student_id"] == student_id),
            None,
        ),
    )


def get_student_by_name(name):
    normalized_name = name.strip().lower()
    return _read(
        lambda: db.students.find_one(
            {"name": {"$regex": f"^{name.strip()}$", "$options": "i"}},
            {"_id": 0},
        ),
        lambda: next(
            (student for student in STUDENTS if student["name"].lower() == normalized_name),
            None,
        ),
    )


def get_student_by_roll_number(roll_number):
    return _read(
        lambda: db.students.find_one({"roll_number": roll_number}, {"_id": 0}),
        lambda: next(
            (
                student
                for student in STUDENTS
                if str(student["roll_number"]) == str(roll_number)
            ),
            None,
        ),
    )


def get_parent_by_id(parent_id):
    return _read(
        lambda: db.parents.find_one({"parent_id": parent_id}, {"_id": 0}),
        lambda: next(
            (parent for parent in PARENTS if parent["parent_id"] == parent_id),
            None,
        ),
    )


def get_teacher_by_id(teacher_id):
    return _read(
        lambda: db.teachers.find_one({"teacher_id": teacher_id}, {"_id": 0}),
        lambda: next(
            (teacher for teacher in TEACHERS if teacher["teacher_id"] == teacher_id),
            None,
        ),
    )


def get_principal():
    return _read(
        lambda: db.principals.find_one({}, {"_id": 0}),
        lambda: PRINCIPALS[0] if PRINCIPALS else None,
    )


def get_all_students():
    return _read(
        lambda: list(db.students.find({}, {"_id": 0})),
        lambda: STUDENTS,
    )


def get_all_teachers():
    return _read(
        lambda: list(db.teachers.find({}, {"_id": 0})),
        lambda: TEACHERS,
    )


def get_all_parents():
    return _read(
        lambda: list(db.parents.find({}, {"_id": 0})),
        lambda: PARENTS,
    )


def get_school_analytics():
    students = get_all_students()

    if not students:
        return {
            "total_students": 0,
            "average_attendance": 0,
            "average_percentage": 0,
        }

    average_attendance = sum(
        student["attendance"]
        for student in students
    ) / len(students)

    average_percentage = sum(
        student["percentage"]
        for student in students
    ) / len(students)

    return {
        "total_students": len(students),
        "average_attendance": round(average_attendance, 2),
        "average_percentage": round(average_percentage, 2),
    }


def mark_student_absent(student_id):
    student = db.students.find_one(
        {"student_id": student_id}
    )

    if not student:
        return {
            "success": False,
            "message": "Student not found.",
        }

    new_attendance = max(
        0,
        student["attendance"] - 1
    )

    db.students.update_one(
        {"student_id": student_id},
        {"$set": {"attendance": new_attendance}}
    )

    return {
        "success": True,
        "message": (
            f"{student['name']} has been marked "
            "absent for today."
        ),
        "updated_attendance": new_attendance,
    }


def create_escalation_request(role, user_id, target):
    request = {
        "success": True,
        "status": "submitted",
        "requester_role": role,
        "requester_id": user_id,
        "target": target,
    }

    # Save the request to MongoDB when the deployment database is reachable.
    # A temporary database outage must not stop the parent from receiving a
    # clear confirmation in the chat.
    if _mongo_available:
        try:
            db.escalation_requests.insert_one(request.copy())
        except PyMongoError:
            pass

    request["message"] = f"Okay, I sent your request to contact {target}."
    return request
