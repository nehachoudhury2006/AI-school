import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_STT_MODEL = os.getenv(
    "GROQ_STT_MODEL",
    "whisper-large-v3-turbo"
)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_TTS_MODEL = os.getenv(
    "ELEVENLABS_TTS_MODEL",
    "eleven_multilingual_v2"
)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

ELEVENLABS_TTS_URL = (
    f"https://api.elevenlabs.io/v1/text-to-speech/"
    f"{ELEVENLABS_VOICE_ID}"
)


def speech_to_text(audio_file_path: str) -> str:
    """Convert audio to text using Groq Whisper."""

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing.")

    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(
            GROQ_STT_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            data={
                "model": GROQ_STT_MODEL,
            },
            files={
                "file": audio_file,
            },
            timeout=120,
        )

    response.raise_for_status()

    result = response.json()

    return result["text"]


def text_to_speech(text: str, output_file_path: str):
    """Convert AI response text to audio using ElevenLabs."""

    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is missing.")

    if not ELEVENLABS_VOICE_ID:
        raise RuntimeError("ELEVENLABS_VOICE_ID is missing.")

    response = requests.post(
        ELEVENLABS_TTS_URL,
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": ELEVENLABS_TTS_MODEL,
        },
        timeout=120,
    )

    response.raise_for_status()

    with open(output_file_path, "wb") as audio_file:
        audio_file.write(response.content)

    return output_file_path