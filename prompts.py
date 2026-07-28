def extraction_prompt(user_message):
    
    return f"""
You are an AI information extractor.

Extract travel information from the user's message.

Return ONLY valid JSON.

The JSON must contain exactly these keys:

{{
    "name": null,
    "destination": null,
    "days": null,
    "budget": null,
    "travelers": null,
    "transport": null
}}

If any information is missing, keep its value as null.

User Message:
{user_message}
"""


def create_travel_prompt(memory,weather):

    return f"""
You are an expert travel planner.

Create a professional travel itinerary.

Trip Details

Name: {memory["name"]}
Destination: {memory["destination"]}
Days: {memory["days"]}
Budget: ₹{memory["budget"]}
Travelers: {memory["travelers"]}
Transport: {memory["transport"]}

Include:

1. Trip Summary
2. Day-wise itinerary
3. Estimated expenses
4. Hotel suggestions
5. Food recommendations
6. Travel tips

Current Weather

Temperature:
{weather["temperature"]}°C

Condition:
{weather["description"]}

Format the answer professionally.
"""