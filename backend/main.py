from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.chat_service import process_chat
from app.chat_service import process_chat
from fastapi import UploadFile, File
from voice_service import speech_to_text, text_to_speech
from mock_api import (
    get_student_by_id,
    get_parent_by_id,
    get_teacher_by_id,
    get_principal,
)

app = FastAPI(title="AVTAR AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AVTAR AI Backend is running!"
    }


@app.get("/students/{student_id}")
def get_student(student_id: str):
    student = get_student_by_id(student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.get("/parents/{parent_id}")
def get_parent(parent_id: str):
    parent = get_parent_by_id(parent_id)

    if parent is None:
        raise HTTPException(
            status_code=404,
            detail="Parent not found"
        )

    return parent


@app.get("/teachers/{teacher_id}")
def get_teacher(teacher_id: str):
    teacher = get_teacher_by_id(teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    return teacher


@app.get("/principal")
def get_principal_data():
    principal = get_principal()

    if principal is None:
        raise HTTPException(
            status_code=404,
            detail="Principal data not found"
        )

    return principal


class ChatRequest(BaseModel):
    message: str
    role: str
    user_id: str


@app.post("/chat")
def chat(request: ChatRequest):

    response = process_chat(
        message=request.message,
        role=request.role,
        user_id=request.user_id,
    )

    return {
        "role": request.role,
        "user_id": request.user_id,
        "message": request.message,
        "response": response,
    }
@app.post("/voice-chat")
async def voice_chat(
    audio: UploadFile = File(...),
    role: str = "student",
    user_id: str = "S001",
):
    audio_path = "temp_input_audio.m4a"

    with open(audio_path, "wb") as file:
        file.write(await audio.read())

    # Audio → Text
    user_text = speech_to_text(audio_path)

    # Text → Ollama → AI response
    ai_response = process_chat(
        message=user_text,
        role=role,
        user_id=user_id,
    )

    return {
        "transcript": user_text,
        "response": ai_response,
    }
