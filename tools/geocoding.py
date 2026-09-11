"""Shared geocoding helper used by the weather and maps tools.

Popular destinations (especially Indian ones that the free geocoder ranks
poorly, e.g. "Goa" -> Genoa) resolve from a small built-in coordinate table.
Everything else falls back to the live Open-Meteo geocoding API, preferring
exact name matches.
"""

import requests

from config import API_TIMEOUT

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Curated coordinates for common travel destinations: (latitude, longitude)
KNOWN_COORDINATES = {
    "goa": (15.2993, 74.1240),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "jaipur": (26.9124, 75.7873),
    "udaipur": (24.5854, 73.7125),
    "jaisalmer": (26.9157, 70.9083),
    "agra": (27.1767, 78.0081),
    "varanasi": (25.3176, 82.9739),
    "amritsar": (31.6340, 74.8723),
    "rishikesh": (30.0869, 78.2676),
    "shimla": (31.1048, 77.1734),
    "manali": (32.2396, 77.1887),
    "mcleodganj": (32.2190, 76.3234),
    "kasol": (32.0090, 77.4220),
    "spiti": (32.2432, 78.0283),
    "leh": (34.1642, 77.5848),
    "ladakh": (34.2268, 77.5619),
    "srinagar": (34.0837, 74.7973),
    "gangtok": (27.3389, 88.6065),
    "darjeeling": (27.0410, 88.2663),
    "shillong": (25.5788, 91.8933),
    "nainital": (29.3803, 79.4636),
    "mussoorie": (30.4597, 78.0665),
    "ooty": (11.4102, 76.6950),
    "kodaikanal": (10.2381, 77.4892),
    "munnar": (10.0889, 77.0595),
    "kochi": (9.9312, 76.2673),
    "kerala": (10.8505, 76.2711),
    "alleppey": (9.4981, 76.3388),
    "hampi": (15.3350, 76.4600),
    "gokarna": (14.5454, 74.3187),
    "puri": (19.8135, 85.8312),
    "pondicherry": (11.9416, 79.8083),
    "puducherry": (11.9416, 79.8083),
    "mahabaleshwar": (17.9217, 73.6055),
    "lonavala": (18.7546, 73.4063),
    "andaman": (11.7401, 92.6586),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "mysore": (12.2958, 76.6394),
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "bangkok": (13.7563, 100.5018),
    "bali": (-8.3405, 115.0920),
    "new york": (40.7128, -74.0060),
}


def get_coordinates(destination: str):
    """Resolve a destination to coordinates.

    Returns {"latitude", "longitude", "name", "country", "source"} or None
    when the place cannot be found at all.
    """
    query = str(destination).strip()
    if not query:
        return None

    known = KNOWN_COORDINATES.get(query.lower())
    if known:
        return {
            "latitude": known[0],
            "longitude": known[1],
            "name": query.title(),
            "country": "",
            "source": "built-in table",
        }

    try:
        response = requests.get(
            GEOCODE_URL,
            params={"name": query, "count": 10, "language": "en", "format": "json"},
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        matches = response.json().get("results") or []
    except (requests.exceptions.RequestException, ValueError):
        return None

    if not matches:
        return None

    # Prefer an exact name match with the largest population, else first hit.
    exact = [m for m in matches if str(m.get("name", "")).lower() == query.lower()]
    candidates = exact or matches
    best = max(candidates, key=lambda m: m.get("population") or 0)

    return {
        "latitude": best.get("latitude"),
        "longitude": best.get("longitude"),
        "name": best.get("name"),
        "country": best.get("country", ""),
        "source": "Open-Meteo geocoding (live)",
    }
