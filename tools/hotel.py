"""Hotel tool - mock provider for development.

The interface matches a real hotel-search API (destination + budget +
travelers + nights -> structured results). To go live, implement
_search_live() against a real provider and switch the call in find_hotels().
Mock results are ALWAYS labeled, so they are never mistaken for live data.
"""

import hashlib

_NAME_SUFFIXES = ["Grand Palace", "Beach Resort", "Garden Inn", "Royal Stay", "Seaview Hotel"]
_AMENITY_SETS = [
    ["Free WiFi", "Breakfast included", "Pool", "Sea view"],
    ["Free WiFi", "AC", "Restaurant", "Room service"],
    ["Free WiFi", "Gym", "Parking", "24x7 front desk"],
    ["Pool", "Spa", "Free cancellation", "Airport shuttle"],
]
_LOCATION_HINTS = ["city centre", "near the main beach", "close to the railway station", "quiet uptown area"]


def _mock_hotels(destination: str, budget, travelers, nights: int) -> list:
    """Deterministic demo hotels so the same destination gives stable data."""
    seed = int(hashlib.sha256(destination.lower().encode()).hexdigest(), 16)
    people = int(travelers) if travelers else 2
    rooms = max(1, (people + 1) // 2)

    if budget and nights:
        target_per_room = (float(budget) * 0.40) / (int(nights) * rooms)
    else:
        target_per_room = 3000

    hotels = []
    for index in range(3):
        jitter = ((seed >> (index * 5)) % 30) - 15  # -15% .. +15%
        price = max(900, int(target_per_room * (1 + jitter / 100)))
        suffix = _NAME_SUFFIXES[(seed + index) % len(_NAME_SUFFIXES)]
        hotels.append({
            "name": f"{destination.title()} {suffix}",
            "price_per_night": price,
            "rating": round(3.8 + ((seed >> index) % 10) / 10, 1),
            "location": f"{destination.title()} - {_LOCATION_HINTS[(seed + index) % len(_LOCATION_HINTS)]}",
            "amenities": _AMENITY_SETS[(seed + index) % len(_AMENITY_SETS)],
            "rooms_needed": rooms,
        })
    return hotels


def find_hotels(destination: str, budget=None, travelers=None, nights=3) -> dict:
    """Return hotel suggestions. Mock/demo data until a live API is added."""
    if not destination or not str(destination).strip():
        return {"status": "error", "error": "Destination is required for hotel search."}

    return {
        "status": "success",
        "source": "mock",
        "mock": True,
        "note": "Demo data for development - connect a real hotel API to get live availability and prices.",
        "destination": str(destination).strip(),
        "nights": nights,
        "hotels": _mock_hotels(str(destination).strip(), budget, travelers, nights),
    }
