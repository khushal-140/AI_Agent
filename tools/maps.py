"""Maps tool: destination coordinates + popular attractions.

Coordinates resolve through the shared geocoding helper (built-in table for
popular destinations, live Open-Meteo geocoding otherwise). The attractions
list is a small built-in DEMO dataset - a real Maps API (Google Places,
Mapbox, etc.) can be added later behind the same interface.
"""

from tools.geocoding import get_coordinates

DEMO_ATTRACTIONS = {
    "goa": [
        {"name": "Baga Beach", "type": "Beach"},
        {"name": "Basilica of Bom Jesus", "type": "Heritage site"},
        {"name": "Dudhsagar Falls", "type": "Waterfall"},
        {"name": "Fort Aguada", "type": "Fort"},
        {"name": "Anjuna Flea Market", "type": "Market"},
    ],
    "jaipur": [
        {"name": "Amber Fort", "type": "Fort"},
        {"name": "Hawa Mahal", "type": "Palace"},
        {"name": "City Palace", "type": "Palace"},
        {"name": "Jantar Mantar", "type": "Observatory"},
    ],
    "delhi": [
        {"name": "Red Fort", "type": "Heritage site"},
        {"name": "India Gate", "type": "Monument"},
        {"name": "Qutub Minar", "type": "Heritage site"},
        {"name": "Lotus Temple", "type": "Temple"},
    ],
    "mumbai": [
        {"name": "Gateway of India", "type": "Monument"},
        {"name": "Marine Drive", "type": "Promenade"},
        {"name": "Elephanta Caves", "type": "Heritage site"},
        {"name": "Juhu Beach", "type": "Beach"},
    ],
    "manali": [
        {"name": "Solang Valley", "type": "Adventure"},
        {"name": "Hadimba Temple", "type": "Temple"},
        {"name": "Old Manali", "type": "Neighbourhood"},
        {"name": "Rohtang Pass", "type": "Mountain pass"},
    ],
    "udaipur": [
        {"name": "City Palace", "type": "Palace"},
        {"name": "Lake Pichola", "type": "Lake"},
        {"name": "Jagdish Temple", "type": "Temple"},
        {"name": "Sajjangarh Monsoon Palace", "type": "Palace"},
    ],
}


def get_place_info(destination: str) -> dict:
    """Return coordinates for the destination plus demo attractions."""
    if not destination or not str(destination).strip():
        return {"status": "error", "error": "Destination is required for maps lookup."}

    place = get_coordinates(str(destination).strip())
    if place is None:
        return {"status": "error", "error": f"Could not find '{destination}'."}

    key = str(destination).strip().lower()
    attractions = DEMO_ATTRACTIONS.get(key, [])

    return {
        "status": "success",
        "source": {
            "coordinates": place.get("source", "geocoding"),
            "attractions": "Built-in demo dataset" if attractions else "not available",
        },
        "destination": place.get("name"),
        "country": place.get("country"),
        "coordinates": {
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude"),
        },
        "attractions": attractions,
        "note": "" if attractions else
        f"Coordinates resolved, but the attractions demo dataset does not include {destination} yet.",
    }
