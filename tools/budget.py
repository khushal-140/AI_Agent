def calculate_budget_per_person(total_budget, travelers):
    """
    Calculate budget per traveler.
    """

    if travelers <= 0:
        return 0

    return total_budget / travelers

