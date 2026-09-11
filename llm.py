"""Thin helpers around the shared Gemini client.

All Gemini calls in the project go through this module so that JSON mode,
markdown code-fence handling and error handling live in exactly one place.
"""

import json
import re

from config import MODEL_NAME, client
from google.genai import types


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the raw text response."""
    response = client.models.***REMOVED***(model=MODEL_NAME, contents=prompt)
    if not response.text:
        raise ValueError("Gemini returned an empty response.")
    return response.text


def ask_gemini_json(prompt: str):
    """Send a prompt that must answer with JSON and return the parsed value."""
    response = client.models.***REMOVED***(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return parse_json(response.text)


def parse_json(text: str):
    """Parse model output as JSON, tolerating markdown code fences.

    Raises ValueError when the text cannot be parsed as JSON.
    """
    if not text:
        raise ValueError("Gemini returned an empty response.")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        newline = cleaned.find("\n")
        if newline != -1:
            cleaned = cleaned[newline + 1 :]
    if cleaned.endswith("```"):
        cleaned = cleaned[: cleaned.rfind("```")]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"[\[{].*[\]}]", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Gemini response was not valid JSON.") from None
