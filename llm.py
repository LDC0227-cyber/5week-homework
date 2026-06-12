import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "deepseek-r1:1.5b"
)


def _ask_ollama(prompt):

    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
            }
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    text = data.get("response", "").strip()

    # DeepSeek-R1의 thinking 제거
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


def chat(system, user, temperature=None):

    prompt = (
        f"{system}\n\n"
        f"{user}\n\n"
        "한국어로 한두 문장만 답하라."
    )

    return _ask_ollama(prompt)


def chat_json(system, user, temperature=0.4):

    prompt = f"""
{system}

{user}

반드시 JSON만 출력하라.
"""

    text = _ask_ollama(prompt)

    try:
        return json.loads(text)

    except Exception:

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:

            try:
                return json.loads(
                    match.group(0)
                )
            except Exception:
                pass

        return {}