from mongo_service import db


def get_student_by_id(student_id):
    return db.students.find_one(
        {"student_id": student_id},
        {"_id": 0}
    )


def get_student_by_name(name):
    return db.students.find_one(
        {"name": {"$regex": f"^{name.strip()}$", "$options": "i"}},
        {"_id": 0}
    )


def get_student_by_roll_number(roll_number):
    return db.students.find_one(
        {"roll_number": roll_number},
        {"_id": 0}
    )


def get_parent_by_id(parent_id):
    return db.parents.find_one(
        {"parent_id": parent_id},
        {"_id": 0}
    )


def get_teacher_by_id(teacher_id):
    return db.teachers.find_one(
        {"teacher_id": teacher_id},
        {"_id": 0}
    )


def get_principal():
    return db.principals.find_one(
        {},
        {"_id": 0}
    )


def get_all_students():
    return list(
        db.students.find({}, {"_id": 0})
    )


def get_all_teachers():
    return list(
        db.teachers.find({}, {"_id": 0})
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
    return {
        "success": True,
        "status": "submitted",
        "requester_role": role,
        "requester_id": user_id,
        "target": target,
        "message": (
            f"Your request to contact {target} "
            "has been submitted."
        ),
    }