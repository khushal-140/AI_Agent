"""Tool registry for the AI Travel Agent.

Every tool is described with metadata (name, description, function,
parameters with types), so the agent executor stays generic: it reads the
metadata instead of containing tool-specific if/elif chains.

To add a new tool: write its function in tools/, describe it here, and add
it to TOOLS. Nothing else needs to change.
"""

from tools.budget import calculate_budget
from tools.currency import convert_currency
from tools.flight import search_flights
from tools.hotel import find_hotels
from tools.maps import get_place_info
from tools.weather import get_weather

WEATHER_TOOL = {
    "name": "weather",
    "description": "Gets current weather and a short forecast for a destination (live data).",
    "function": get_weather,
    "parameters": [
        {"name": "destination", "type": str},
    ],
}

BUDGET_TOOL = {
    "name": "budget",
    "description": "Splits the total trip budget per traveler and gives an estimated category breakdown.",
    "function": calculate_budget,
    "parameters": [
        {"name": "budget", "type": float},
        {"name": "travelers", "type": int},
    ],
}

HOTEL_TOOL = {
    "name": "hotel",
    "description": "Suggests hotels in the destination with prices, ratings and amenities (demo data unless a live API is configured).",
    "function": find_hotels,
    "parameters": [
        {"name": "destination", "type": str},
        {"name": "budget", "type": float},
        {"name": "travelers", "type": int},
        {"name": "nights", "type": int, "memory_key": "days", "default": 3},
    ],
}

FLIGHT_TOOL = {
    "name": "flight",
    "description": "Searches flights from an origin city to the destination with group pricing (demo data unless a live API is configured).",
    "function": search_flights,
    "parameters": [
        {"name": "origin", "type": str},
        {"name": "destination", "type": str},
        {"name": "travelers", "type": int, "default": 1},
        {"name": "travel_class", "type": str, "default": "economy"},
    ],
}

MAPS_TOOL = {
    "name": "maps",
    "description": "Finds the destination's coordinates (live geocoding) and popular attractions (demo dataset).",
    "function": get_place_info,
    "parameters": [
        {"name": "destination", "type": str},
    ],
}

CURRENCY_TOOL = {
    "name": "currency",
    "description": "Converts an amount between currencies, e.g. USD to INR, using live exchange rates.",
    "function": convert_currency,
    "parameters": [
        {"name": "amount", "type": float, "default": 1.0},
        {"name": "from_currency", "type": str, "default": "USD"},
        {"name": "to_currency", "type": str, "default": "INR"},
    ],
}

TOOLS = {
    "weather": WEATHER_TOOL,
    "budget": BUDGET_TOOL,
    "hotel": HOTEL_TOOL,
    "flight": FLIGHT_TOOL,
    "maps": MAPS_TOOL,
    "currency": CURRENCY_TOOL,
}
