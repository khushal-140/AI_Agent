"""Budget tool: splits the trip budget across travelers and categories."""

CATEGORY_SHARES = {
    "hotel": 0.40,
    "food": 0.25,
    "transportation": 0.20,
    "activities": 0.10,
    "miscellaneous": 0.05,
}


def calculate_budget(budget: float, travelers: int) -> dict:
    """Split `budget` across `travelers` and return an estimated breakdown."""
    if budget is None or budget <= 0:
        return {"status": "error", "error": "Budget must be a positive amount."}
    if travelers is None or travelers <= 0:
        return {"status": "error", "error": "Number of travelers must be at least 1."}

    budget = float(budget)
    travelers = int(travelers)
    per_person = round(budget / travelers, 2)
    breakdown = {name: round(budget * share, 2) for name, share in CATEGORY_SHARES.items()}
    remaining = round(budget - sum(breakdown.values()), 2)

    return {
        "status": "success",
        "source": "calculated",
        "total_budget": budget,
        "travelers": travelers,
        "budget_per_person": per_person,
        "breakdown": breakdown,
        "remaining": remaining,
        "note": "Planning split: hotel 40%, food 25%, transport 20%, activities 10%, miscellaneous 5%.",
    }
