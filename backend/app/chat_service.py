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


def process_chat(
    message: str,
    role: str,
    user_id: str,
):
    # The frontend may send prior messages for context. The final question is
    # the part that should decide intent and any school-data lookup.
    if "\n\nNew user message:" in message:
        message = message.rsplit("\n\nNew user message:", 1)[1].strip()

    message_lower = message.lower().strip()

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

    # -------------------------
    # STUDENT
    # -------------------------
    if role.lower() == "student":
        student = get_student_by_id(user_id)

        if not student:
            return "I could not find your student account."

        if any(word in message_lower for word in [
            "attendance",
            "present",
            "absent"
        ]):
            context = {
                "name": student["name"],
                "attendance": student["attendance"],
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
            }

        prompt = f"""
You are AVTAR AI, a friendly school assistant.

The current user is a STUDENT.
They are authorized to access ONLY their own information.

Student data:
{context}

User question:
{message}

Answer naturally and accurately.
Answer only the user's question. Keep the answer to 1-2 short sentences.
Do not mention the principal, doctor, or any unrelated person unless asked.
Never invent information.
Do not expose other students' private data.
"""

        return chat_with_ollama(prompt)

    # -------------------------
    # PARENT
    # -------------------------
    if role.lower() == "parent":
        parent = get_parent_by_id(user_id)

        if not parent:
            return "I could not find your parent account."

        # Escalation request
        if (
    "teacher" in message_lower
    and (
        "talk" in message_lower
        or "speak" in message_lower
        or "contact" in message_lower
        or "connect" in message_lower
    )
):
            return (
                "Of course. I can submit a request to contact "
                "your child's teacher. Would you like me to submit it?"
            )

        student = get_student_by_id(parent["child_id"])

        if not student:
            return "I could not find the linked child record."

        context = {
            "parent": parent["parent_name"],
            "child": student["name"],
            "attendance": student["attendance"],
            "marks": student["marks"],
            "total_marks": student["total_marks"],
            "percentage": student["percentage"],
            "grade": student["grade"],
            "rank": student["rank"],
        }

        prompt = f"""
You are AVTAR AI, a caring and patient Parent Support Assistant.

The current user is a PARENT.
They are authorized to access ONLY their linked child's information.

Parent/child data:
{context}

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
    if role.lower() == "teacher":
        teacher = get_teacher_by_id(user_id)

        if not teacher:
            return "I could not find your teacher account."

        if "mark" in message_lower and "absent" in message_lower:
            student = find_student_from_message(message)

            if not student:
                return "Please tell me the student's name or roll number."

            result = mark_student_absent(student["student_id"])
            return result["message"]

        student = find_student_from_message(message)

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
            }

        prompt = f"""
You are AVTAR AI, a professional Teaching Assistant.

The current user is a TEACHER.
They may access information for students assigned to them.
They may perform authorized attendance actions.

Teacher context:
{context}

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
    if role.lower() == "principal":
        principal = get_principal()

        if not principal:
            return "Principal information is unavailable."

        teachers = get_all_teachers()

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

        analytics = get_school_analytics()

        context = {
            "principal": principal["name"],
            "school": principal["school_name"],
            "total_students": analytics["total_students"],
            "average_attendance": analytics["average_attendance"],
            "average_percentage": analytics["average_percentage"],
        }

        prompt = f"""
You are AVTAR AI, a professional Management Assistant.

The current user is the PRINCIPAL.
The principal is authorized to access school-wide analytics.

School data:
{context}

User question:
{message}

Answer naturally and accurately.
Answer only the user's question in 1-2 short sentences.
Do not add unrelated details or names.
Never invent statistics.
"""

        return chat_with_ollama(prompt)

    return "Invalid role. Please use Student, Parent, Teacher, or Principal."
