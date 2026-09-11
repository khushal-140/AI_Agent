"""Conversation handling: information extraction and missing-detail questions."""

from llm import ask_gemini, ask_gemini_json
from memory import ALL_FIELDS, MEMORY_FIELDS, normalize_field
from prompts import extraction_prompt, missing_info_prompt

FIELD_QUESTIONS = {
    "name": "What is your name?",
    "destination": "Which destination would you like to visit?",
    "days": "How many days will your trip be?",
    "budget": "What is your total budget (in ₹)?",
    "travelers": "How many travelers are going?",
    "transport": "How would you like to travel (flight, train, bus or car)?",
}


def get_missing_fields(memory: dict) -> list:
    """Return the required fields that have no value yet."""
    return [field for field in MEMORY_FIELDS if memory.get(field) in (None, "")]


def extract_information(user_message: str) -> dict:
    """Ask Gemini to extract trip details from a message.

    Returns only the fields genuinely found in the message; on any failure
    returns an empty dict so the conversation can continue.
    """
    try:
        data = ask_gemini_json(extraction_prompt(user_message))
    except Exception:
        return {}  # never crash the conversation over a failed extraction

    if not isinstance(data, dict):
        return {}

    extracted = {}
    for field in ALL_FIELDS:
        value = data.get(field)
        if value in (None, ""):
            continue
        try:
            extracted[field] = normalize_field(field, value)
        except (ValueError, TypeError):
            continue
    return extracted


def build_missing_question(missing_fields: list) -> str:
    """Static fallback question listing everything still missing."""
    questions = [FIELD_QUESTIONS[field] for field in missing_fields]
    return "To plan your trip, I still need to know: " + " ".join(questions)


def generate_missing_question(user_message: str, memory: dict, missing_fields: list) -> str:
    """A natural, Gemini-phrased question for only the missing details."""
    try:
        reply = ask_gemini(missing_info_prompt(user_message, memory, missing_fields))
        if reply and reply.strip():
            return reply.strip()
    except Exception:
        pass
    return build_missing_question(missing_fields)


def validate_answer(field: str, answer: str):
    """Validate one CLI answer. Returns (value, None) or (None, error message)."""
    if not answer:
        return None, "Please enter a value."
    try:
        return normalize_field(field, answer), None
    except (ValueError, TypeError):
        if field in ("days", "travelers"):
            return None, "Please enter a whole number greater than 0."
        if field == "budget":
            return None, "Please enter a valid amount, for example 30000."
        return None, "Please enter a valid value."


def ask_missing_information(memory: dict) -> dict:
    """CLI helper: interactively ask for each missing field (with validation)."""
    for field in MEMORY_FIELDS:
        if memory.get(field) is not None:
            continue  # never re-ask for information already provided
        question = FIELD_QUESTIONS[field]
        while True:
            answer = input(f"AI: {question} ").strip()
            value, error = validate_answer(field, answer)
            if error is None:
                memory[field] = value
                break
            print(f"AI: {error}")
    return memory
