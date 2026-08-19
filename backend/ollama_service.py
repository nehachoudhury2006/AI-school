import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")

OLLAMA_URL = "https://ollama.com/api/chat"


def chat_with_ollama(message: str):
    response = requests.post(
        OLLAMA_URL,
        headers={
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "stream": False,
        },
        # Do not leave the chat waiting for two minutes if the cloud model is
        # slow or temporarily unavailable.
        timeout=25,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]
