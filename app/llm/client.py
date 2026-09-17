from groq import Groq

from app.config import GROQ_API_KEY


client = Groq(api_key=GROQ_API_KEY)

def generate_response(messages: list[dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    return response.choices[0].message.content or ""

import json


def extract_booking_details(question: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "Extract interview booking information from the user's message. "
                "Return ONLY a JSON object with exactly these keys: "
                "name, email, date, time. "
                "Use null for information that is not provided. "
                "Do not invent or guess information."
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"

    return json.loads(content)


def detect_booking_intent(question: str) -> bool:
    messages = [
        {
            "role": "system",
            "content": (
                "Determine whether the user wants to book or schedule an interview. "
                "Return ONLY a JSON object with this key: booking_intent. "
                "The value must be true or false."
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"

    result = json.loads(content)

    return bool(result.get("booking_intent", False))