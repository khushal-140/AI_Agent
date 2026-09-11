"""Command-line interface for the AI Travel Agent.

Run with:  python main.py   (or:  python travel_agent.py)
"""

from agent_executor import plan_trip, process_message
from conversation import ask_missing_information, get_missing_fields
from memory import new_memory


def _format_memory(memory: dict) -> str:
    lines = [
        f"  {field.capitalize():<12}: {value}"
        for field, value in memory.items()
        if value not in (None, "")
    ]
    return "\n".join(lines)


def _print_itinerary(itinerary: dict) -> None:
    if itinerary.get("raw"):
        if itinerary.get("raw_text"):
            print(itinerary["raw_text"])
        return

    print("\n--- Trip Summary ---")
    print(itinerary.get("trip_summary", ""))

    print("\n--- Day-by-Day Plan ---")
    for day in itinerary.get("days", []):
        print(f"\nDay {day.get('day')}: {day.get('title', '')}")
        print(f"  Morning  : {day.get('morning', '')}")
        print(f"  Afternoon: {day.get('afternoon', '')}")
        print(f"  Evening  : {day.get('evening', '')}")

    budget = itinerary.get("budget_breakdown", {})
    if budget:
        print("\n--- Estimated Budget (estimate) ---")
        for category, amount in budget.items():
            print(f"  {category.capitalize():<15}: Rs {amount}")

    food = itinerary.get("food_recommendations", [])
    if food:
        print("\n--- Food Recommendations ---")
        for item in food:
            print(f"  - {item}")

    tips = itinerary.get("travel_tips", [])
    if tips:
        print("\n--- Travel Tips ---")
        for item in tips:
            print(f"  - {item}")


def run_travel_agent() -> None:
    print("=" * 46)
    print("          AI TRAVEL AGENT")
    print("       Plan smarter. Travel better.")
    print("=" * 46)
    print("AI: Hi! Tell me about your trip. Type 'exit' to quit.")

    memory = new_memory()

    while True:
        try:
            user_message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAI: Goodbye! Happy travels! ✈️")
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit", "bye"}:
            print("AI: Goodbye! Happy travels! ✈️")
            break

        result = process_message(memory, user_message)

        if result["status"] == "need_info":
            print(f"\nAI: {result['reply']}")
            # In the CLI we fill remaining gaps interactively, asking only
            # for the fields that are still missing.
            ask_missing_information(memory)
            if get_missing_fields(memory):
                continue
            result = plan_trip(memory, user_message)

        if result["status"] == "error":
            print(f"\nAI: {result['reply']}")
            continue

        print("\nAI:", result["reply"])
        print("\n" + "=" * 46)
        print("YOUR TRIP DETAILS")
        print("=" * 46)
        print(_format_memory(memory))
        print("\n" + "=" * 46)
        print("YOUR AI TRAVEL PLAN")
        print("=" * 46)
        _print_itinerary(result["itinerary"])
        print("\nAI: Want to plan another trip? Just describe it, or type 'exit'.")


if __name__ == "__main__":
    run_travel_agent()
