import re

from ollama_service import chat_with_ollama
from mock_api import (
    get_student_by_id,
    get_student_by_name,
    get_student_by_roll_number,
    get_parent_by_id,
    get_teacher_by_id,
    get_principal,
    get_school_analytics,
    mark_student_absent,
    create_escalation_request,
    get_all_students,
    get_all_parents,
    get_all_teachers,
)


def find_student_from_message(message: str):
    match = re.search(r"\b(10[1-9]|11[0-9]|120)\b", message)

    if match:
        student = get_student_by_roll_number(match.group(1))
        if student:
            return student

    students = [
        "Aarav Sharma",
        "Anaya Patel",
        "Vihaan Mehta",
        "Ishita Verma",
        "Aditya Singh",
        "Myra Nair",
        "Arjun Iyer",
        "Sara Khan",
        "Kabir Joshi",
        "Diya Kapoor",
        "Reyansh Das",
        "Aanya Gupta",
        "Rohan Kulkarni",
        "Meera Shah",
        "Kiaan Rao",
        "Navya Reddy",
        "Dhruv Bansal",
        "Ira Thomas",
        "Yash Malhotra",
        "Anvi Menon",
    ]

    message_lower = message.lower()

    for name in students:
        if name.lower() in message_lower:
            return get_student_by_name(name)

    return None


def is_self_question(message_lower: str) -> bool:
    return any(phrase in message_lower for phrase in [
        "who am i", "what is my name", "what's my name", "my name",
        "what is my role", "what's my role", "my role", "mera naam",
        "main kaun hoon", "mera role", "मैं कौन हूँ", "मेरा नाम",
        "मेरा रोल",
    ])


def find_teacher_from_message(message: str):
    message_lower = message.lower()

    for teacher in get_all_teachers():
        if (
            teacher["name"].lower() in message_lower
            or teacher["subject"].lower() in message_lower
        ):
            return teacher

    return None


def is_teacher_contact_request(message_lower: str) -> bool:
    """Only explicit, present-message commands may create a contact request."""
    mentions_teacher = "teacher" in message_lower or find_teacher_from_message(
        message_lower
    ) is not None
    contact_command = re.search(
        r"\b(talk|speak|connect)\s+(to|with)\b|\b(contact|message|request)\b|"
        r"teacher\s+se\s+baat|teacher\s+ko\s+message",
        message_lower,
    )
    return bool(mentions_teacher and contact_command)


def is_school_data_question(message_lower: str) -> bool:
    """Decide when a question needs protected school records."""
    school_keywords = [
        "attendance", "present", "absent", "mark", "marks", "score",
        "percentage", "grade", "rank", "roll", "student", "parent",
        "teacher", "principal", "class", "school", "my child", "my child",
        "my son", "my daughter", "my subject", "my result", "my results",
        "report card", "homework", "timetable", "admission",
    ]
    return any(keyword in message_lower for keyword in school_keywords)


def answer_general_question(message: str, conversation_context: str) -> str:
    """Answer non-school questions without exposing school account data."""
    prompt = f"""
You are AVTAR AI, a friendly and helpful assistant.

The user asked a general-knowledge question that is unrelated to private
school records. Answer it directly and naturally in 1-2 short sentences.
Use the recent conversation only to resolve references such as "it" or
"that". Do not mention or reveal any school, student, parent, teacher, or
principal data unless the user explicitly asks a school-data question.

Recent conversation in this same chat:
{conversation_context or "No previous messages."}

User question:
{message}
"""
    return chat_with_ollama(prompt)


def teacher_students(teacher):
    assigned_ids = set(teacher.get("students_assigned", []))
    return [
        student for student in get_all_students()
        if student["student_id"] in assigned_ids
    ]


def resolve_role(role: str, user_id: str) -> str:
    """Prefer an unambiguous account ID over a stale browser role value."""
    normalized_role = role.strip().lower()
    normalized_id = user_id.strip().upper()

    if normalized_id.startswith("PR"):
        return "principal"
    if normalized_id.startswith("T"):
        return "teacher"
    if normalized_id.startswith("P"):
        return "parent"
    if normalized_id.startswith("S") or normalized_id.isdigit():
        return "student"

    return normalized_role


def get_logged_in_identity(role: str, user_id: str):
    """Return a deterministic identity answer from the authorized account."""
    if role == "student":
        student = get_student_by_id(user_id) or get_student_by_roll_number(user_id)
        if not student:
            return "I could not find your student account."
        return f"You are {student['name']}, a student in class {student['class']}."

    if role == "parent":
        parent = get_parent_by_id(user_id)
        if not parent:
            return "I could not find your parent account."
        return (
            f"You are {parent['parent_name']}, the "
            f"{parent['relationship'].lower()} of {parent['child_name']}."
        )

    if role == "teacher":
        teacher = get_teacher_by_id(user_id)
        if not teacher:
            return "I could not find your teacher account."
        return f"You are {teacher['name']}, the {teacher['subject']} teacher."

    if role == "principal":
        principal = get_principal()
        if not principal:
            return "Principal information is unavailable."
        return (
            f"You are {principal['name']}, the principal of "
            f"{principal['school_name']}."
        )

    return "I could not identify your account role."


def process_chat(
    message: str,
    role: str,
    user_id: str,
):
    # Keep only this chat's recent history. The frontend starts a new empty
    # history for New Chat, so context never crosses into a new conversation.
    conversation_context = ""
    if "\n\nNew user message:" in message:
        conversation_context, message = message.rsplit(
            "\n\nNew user message:", 1
        )
        conversation_context = conversation_context.replace(
            "Previous conversation:\n", "", 1
        ).strip()
        message = message.strip()

    message_lower = message.lower().strip()
    role = resolve_role(role, user_id)

    # Common conversational questions do not need a database or an external
    # model call. This gives an immediate, consistent answer.
    identity_questions = [
        "who are you", "what are you", "what can you do",
        "how can you help", "tum kaun ho", "tu kaun hai",
        "aap kaun ho", "aap kaun hain", "tum kon ho",
        "तू कौन हो", "तुम कौन हो", "आप कौन हो", "आप कौन हैं",
    ]

    if any(phrase in message_lower for phrase in identity_questions):
        return "I'm AVTAR AI, your school learning assistant."

    if message_lower in {"hi", "hello", "hey", "hii"}:
        return (
            "Hello! I'm AVTAR AI. How can I help you with your "
            "school information today?"
        )

    # These must run before general knowledge routing. They refer to the
    # logged-in account and therefore require exact authorized data, not an
    # Ollama inference.
    if is_self_question(message_lower):
        if "role" in message_lower or "रोल" in message_lower:
            return f"You are a {role}."
        return get_logged_in_identity(role, user_id)

    # General knowledge must not be restricted by the privacy rules applied
    # to school records. Role-specific paths below are used only when a
    # protected school-data keyword is present.
    if not is_school_data_question(message_lower):
        return answer_general_question(message, conversation_context)

    # -------------------------
    # STUDENT
    # -------------------------
    if role == "student":
        # The profile form asks students for their roll number, while some
        # records use IDs such as S001. Support both forms of the same user.
        student = (
            get_student_by_id(user_id)
            or get_student_by_roll_number(user_id)
        )

        if not student:
            return "I could not find your student account."

        if is_self_question(message_lower):
            if "role" in message_lower or "रोल" in message_lower:
                return "You are a student."
            return f"You are {student['name']}, a student in class {student['class']}."

        if any(word in message_lower for word in [
            "attendance",
            "present",
            "absent"
        ]):
            context = {
                "name": student["name"],
                "attendance": student["attendance"],
                "percentage": student["percentage"],
            }

        elif any(word in message_lower for word in [
            "mark",
            "marks",
            "score",
            "percentage",
            "grade",
            "math",
            "science",
            "english",
            "computer",
            "social"
        ]):
            context = {
                "name": student["name"],
                "math": student["marks"]["math"],
                "science": student["marks"]["science"],
                "english": student["marks"]["english"],
                "computer": student["marks"]["computer"],
                "social_science": student["marks"]["social_science"],
                "total_marks": student["total_marks"],
                "percentage": student["percentage"],
                "grade": student["grade"],
                "rank": student["rank"],
            }

        else:
            context = {
                "name": student["name"],
                "roll_number": student["roll_number"],
                "class": student["class"],
                "attendance": student["attendance"],
                "percentage": student["percentage"],
                "grade": student["grade"],
                "teachers": [
                    {"name": teacher["name"], "subject": teacher["subject"]}
                    for teacher in get_all_teachers()
                ],
            }

        prompt = f"""
You are AVTAR AI, a friendly school assistant.

The current user is a STUDENT.
They are authorized to access ONLY their own information.

Student data:
{context}

Recent conversation in this same chat:
{conversation_context or "No previous messages."}

User question:
{message}

Answer naturally and accurately.
Answer only the user's question. Keep the answer to 1-2 short sentences.
Treat every value in Student data as exact. If asked about attendance or
percentage, state the corresponding value exactly; never infer one from the other.
Do not mention the principal, doctor, or any unrelated person unless asked.
Never invent information.
Do not expose other students' private data.
"""

        return chat_with_ollama(prompt)

    # -------------------------
    # PARENT
    # -------------------------
    if role == "parent":
        parent = get_parent_by_id(user_id)

        if not parent:
            return "I could not find your parent account."

        if is_self_question(message_lower):
            if "role" in message_lower or "रोल" in message_lower:
                return "You are a parent."
            return f"You are {parent['parent_name']}, the {parent['relationship'].lower()} of {parent['child_name']}."

        # Contact requests are recorded before the assistant confirms them.
        if is_teacher_contact_request(message_lower):
            teacher = find_teacher_from_message(message)
            target = (
                f"{teacher['name']}, the {teacher['subject']} teacher"
                if teacher
                else "your child's teacher"
            )
            result = create_escalation_request("parent", parent["parent_id"], target)
            return result["message"]

        student = get_student_by_id(parent["child_id"])

        if not student:
            return "I could not find the linked child record."

        linked_teachers = [
            {
                "name": teacher["name"],
                "subject": teacher["subject"],
            }
            for teacher in get_all_teachers()
            if teacher["teacher_id"] in student.get("teacher_ids", [])
        ]
        principal = get_principal()

        context = {
            "parent": parent["parent_name"],
            "child": student["name"],
            "attendance": student["attendance"],
            "marks": student["marks"],
            "total_marks": student["total_marks"],
            "percentage": student["percentage"],
            "grade": student["grade"],
            "rank": student["rank"],
            "child_teachers": linked_teachers,
            "principal": principal["name"] if principal else None,
        }

        prompt = f"""
You are AVTAR AI, a caring and patient Parent Support Assistant.

The current user is a PARENT.
They are authorized to access ONLY their linked child's information.

Parent/child data:
{context}

Recent conversation in this same chat:
{conversation_context or "No previous messages."}

User question:
{message}

Answer naturally.
Answer only the user's question in 1-2 short sentences.
Do not add unrelated details or names.
Never expose information about another child.
Never invent data.
"""

        return chat_with_ollama(prompt)

    # -------------------------
    # TEACHER
    # -------------------------
    if role == "teacher":
        teacher = get_teacher_by_id(user_id)

        if not teacher:
            return "I could not find your teacher account."

        if is_self_question(message_lower):
            if "role" in message_lower or "रोल" in message_lower:
                return "You are a teacher."
            return f"You are {teacher['name']}, the {teacher['subject']} teacher."

        assigned_students = teacher_students(teacher)

        if "mark" in message_lower and "absent" in message_lower:
            student = find_student_from_message(message)

            if not student:
                return "Please tell me the student's name or roll number."

            if student["student_id"] not in teacher.get("students_assigned", []):
                return "You can only update attendance for students assigned to you."

            result = mark_student_absent(student["student_id"])
            return result["message"]

        student = find_student_from_message(message)

        if student and student["student_id"] not in teacher.get("students_assigned", []):
            return "You can only view information for students assigned to you."

        if student:
            if "name" in message_lower:
                return f"Roll number {student['roll_number']} belongs to {student['name']}."
            if any(word in message_lower for word in ["mark", "marks", "score"]):
                marks = ", ".join(
                    f"{subject.title()}: {score}"
                    for subject, score in student["marks"].items()
                )
                return f"{student['name']}'s marks are {marks}."
            if "attendance" in message_lower:
                return f"{student['name']}'s attendance is {student['attendance']}%."
            if "percentage" in message_lower:
                return f"{student['name']}'s percentage is {student['percentage']}%."
            if "roll" in message_lower:
                return f"{student['name']}'s roll number is {student['roll_number']}."

        if not student and any(word in message_lower for word in [
            "students", "student names", "class list", "roll number", "roll numbers",
        ]):
            student_list = ", ".join(
                f"{item['name']} (roll {item['roll_number']})"
                for item in assigned_students
            )
            return f"Your assigned students are: {student_list}."

        if student:
            context = {
                "teacher": teacher["name"],
                "subject": teacher["subject"],
                "student": student["name"],
                "student_class": student["class"],
                "attendance": student["attendance"],
                "marks": student["marks"],
                "percentage": student["percentage"],
                "grade": student["grade"],
            }
        else:
            context = {
                "teacher": teacher["name"],
                "subject": teacher["subject"],
                "classes_handled": teacher["classes_handled"],
                "assigned_students": [
                    {
                        "name": item["name"],
                        "roll_number": item["roll_number"],
                        "marks": item["marks"],
                        "attendance": item["attendance"],
                    }
                    for item in assigned_students
                ],
            }

        prompt = f"""
You are AVTAR AI, a professional Teaching Assistant.

The current user is a TEACHER.
They may access information for students assigned to them.
They may perform authorized attendance actions.

Teacher context:
{context}

Recent conversation in this same chat:
{conversation_context or "No previous messages."}

User question:
{message}

Answer naturally.
Answer only the user's question in 1-2 short sentences.
Do not add unrelated details or names.
Do not expose unrelated private data.
Do not claim an action succeeded unless the mock service confirms it.
"""

        return chat_with_ollama(prompt)

    # -------------------------
    # PRINCIPAL
    # -------------------------
    if role == "principal":
        principal = get_principal()

        if not principal:
            return "Principal information is unavailable."

        if is_self_question(message_lower):
            if "role" in message_lower or "रोल" in message_lower:
                return "You are the principal."
            return f"You are {principal['name']}, the principal of {principal['school_name']}."

        teachers = get_all_teachers()
        students = get_all_students()
        parents = get_all_parents()

        # Give principals exact teacher information directly from the school
        # data instead of relying on the language model to infer it.
        if "teacher" in message_lower:
            count_words = [
                "how many", "count", "total", "kitne", "kitna",
                "कितने", "कितना",
            ]

            if any(word in message_lower for word in count_words):
                return f"There are {len(teachers)} teachers in the school."

            teacher_details = ", ".join(
                f"{teacher['name']} ({teacher['subject']})"
                for teacher in teachers
            )
            return f"Teachers: {teacher_details}."

        if any(word in message_lower for word in ["student", "roll number", "roll numbers"]):
            student_details = ", ".join(
                f"{student['name']} (roll {student['roll_number']})"
                for student in students
            )
            return f"Students: {student_details}."

        if "parent" in message_lower:
            parent_details = ", ".join(
                f"{parent['parent_name']} ({parent['relationship']} of {parent['child_name']})"
                for parent in parents
            )
            return f"Parents: {parent_details}."

        analytics = get_school_analytics()

        context = {
            "principal": principal["name"],
            "school": principal["school_name"],
            "total_students": analytics["total_students"],
            "average_attendance": analytics["average_attendance"],
            "average_percentage": analytics["average_percentage"],
            "teachers": [
                {"name": teacher["name"], "subject": teacher["subject"]}
                for teacher in teachers
            ],
            "students": [
                {
                    "name": student["name"],
                    "roll_number": student["roll_number"],
                    "class": student["class"],
                    "attendance": student["attendance"],
                    "percentage": student["percentage"],
                }
                for student in students
            ],
            "parents": [
                {
                    "name": parent["parent_name"],
                    "child": parent["child_name"],
                    "relationship": parent["relationship"],
                }
                for parent in parents
            ],
        }

        prompt = f"""
You are AVTAR AI, a professional Management Assistant.

The current user is the PRINCIPAL.
The principal is authorized to access school-wide analytics.

School data:
{context}

Recent conversation in this same chat:
{conversation_context or "No previous messages."}

User question:
{message}

Answer naturally and accurately.
Answer only the user's question in 1-2 short sentences.
Do not add unrelated details or names.
Never invent statistics.
The principal is authorized to access the school-wide data supplied above.
"""

        return chat_with_ollama(prompt)

    return "Invalid role. Please use Student, Parent, Teacher, or Principal."
