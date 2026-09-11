"""Conversation memory for the AI Travel Agent.

Memory holds everything the agent knows about the current trip. Known values
are never overwritten with None or empty strings, so a follow-up message like
"I have a budget of 30,000" only fills in the budget and keeps the rest.
"""

import re

MEMORY_FIELDS = ["name", "destination", "days", "budget", "travelers", "transport"]
# Optional detail: stored when the user mentions it, never asked for.
OPTIONAL_FIELDS = ["origin"]
ALL_FIELDS = MEMORY_FIELDS + OPTIONAL_FIELDS
INT_FIELDS = {"days", "travelers"}
FLOAT_FIELDS = {"budget"}


def new_memory() -> dict:
    """Return a fresh memory dict for a new conversation."""
    return {field: None for field in ALL_FIELDS}


def normalize_field(field: str, value):
    """Coerce user/model input to the right type, or raise ValueError."""
    text = str(value).strip()
    if not text:
        raise ValueError("value is empty")

    if field in INT_FIELDS:
        number = int(float(re.sub(r"[^\d.]", "", text) or "0"))
        if number <= 0:
            raise ValueError(f"{field} must be a whole number greater than 0")
        return number

    if field in FLOAT_FIELDS:
        amount = float(re.sub(r"[^\d.]", "", text) or "0")
        if amount <= 0:
            raise ValueError("budget must be greater than 0")
        return amount

    if field == "transport":
        return text.lower()

    return text


def update_memory(memory: dict, extracted: dict | None) -> dict:
    """Merge newly extracted details into memory.

    Existing values are never replaced with None/empty - only real new
    information updates the memory.
    """
    for field in ALL_FIELDS:
        value = (extracted or {}).get(field)
        if value in (None, ""):
            continue
        try:
            memory[field] = normalize_field(field, value)
        except (ValueError, TypeError):
            continue  # ignore malformed values instead of crashing
    return memory


def is_complete(memory: dict) -> bool:
    """True when every required field has a value."""
    return all(memory.get(field) not in (None, "") for field in MEMORY_FIELDS)
