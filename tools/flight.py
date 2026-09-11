"""Flight tool - mock provider for development.

The interface matches a real flight-search API (origin, destination,
travelers, class -> priced options). To go live, implement _search_live()
against a provider such as Amadeus or Skyscanner and switch the call in
search_flights(). Demo results use FICTIONAL airline names and are ALWAYS
labeled, so they are never mistaken for live fares.
"""

import hashlib

_CLASS_MULTIPLIERS = {"economy": 1.0, "premium economy": 1.6, "business": 2.8, "first": 4.0}
_DEMO_AIRLINES = ["SkyWings (demo)", "IndiJet (demo)", "AeroLink (demo)"]
_AIRLINE_FACTORS = [0.92, 1.0, 1.08]


def search_flights(origin: str, destination: str, travelers=1, travel_class="economy") -> dict:
    """Return demo flight options between origin and destination."""
    if not origin or not str(origin).strip():
        return {"status": "error", "error": "Origin city is required for flight search."}
    if not destination or not str(destination).strip():
        return {"status": "error", "error": "Destination is required for flight search."}

    try:
        people = int(travelers)
    except (TypeError, ValueError):
        return {"status": "error", "error": "Travelers must be a whole number."}
    if people <= 0:
        return {"status": "error", "error": "At least one traveler is required."}

    cabin = str(travel_class or "economy").strip().lower()
    multiplier = _CLASS_MULTIPLIERS.get(cabin, 1.0)

    seed = int(hashlib.sha256(f"{origin.lower()}-{destination.lower()}".encode()).hexdigest(), 16)
    base_fare = 2200 + (seed % 6800)  # demo base fare: Rs 2,200 - Rs 8,999
    price_per_person = round(base_fare * multiplier, 2)

    options = [
        {
            "airline": _DEMO_AIRLINES[index],
            "price_per_person": round(price_per_person * _AIRLINE_FACTORS[index], 2),
            "total_for_group": round(price_per_person * _AIRLINE_FACTORS[index] * people, 2),
        }
        for index in range(len(_DEMO_AIRLINES))
    ]

    return {
        "status": "success",
        "source": "mock",
        "mock": True,
        "note": "Demo data for development - airline names are fictional. Connect a real flight API for live fares.",
        "origin": str(origin).strip().title(),
        "destination": str(destination).strip().title(),
        "travel_class": cabin,
        "travelers": people,
        "price_per_person": price_per_person,
        "total_price": round(price_per_person * people, 2),
        "flights": options,
    }
