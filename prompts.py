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


def tool_selection_prompt(user_message):

    return f"""
You are an AI Tool Router.

Available Tools:

1. weather
Use when the user asks about:
- weather
- rain
- climate
- temperature
- umbrella
- hot or cold
- forecast

2. budget
Use when the user asks about:
- budget
- expenses
- cost
- split budget
- per person cost

Return ONLY valid JSON.

Example:

{{
    "tools": ["weather"]
}}

If no tool is required:

{{
    "tools": []
}}

User Request:

{user_message}
"""


def create_travel_prompt(memory, tool_results):
    weather_info = ""
    budget_info = ""

    if "weather" in tool_results:
        weather = tool_results["weather"]

        weather_info = f"""
Current Weather
---------------
Temperature : {weather['temperature']}°C
Condition   : {weather['description']}
"""

    if "budget" in tool_results:

        budget_info = f"""
Budget Per Person
-----------------
₹{tool_results['budget']:.2f}
"""

    return f"""
You are an expert travel planner.

Create a professional travel itinerary.

Traveler Details
----------------
Name        : {memory['name']}
Destination : {memory['destination']}
Days        : {memory['days']}
Budget      : ₹{memory['budget']}
Travelers   : {memory['travelers']}
Transport   : {memory['transport']}

{weather_info}

{budget_info}

Please include:

1. Trip Summary
2. Day-wise Itinerary
3. Estimated Expenses
4. Hotel Suggestions
5. Food Recommendations
6. Travel Tips

Write the response professionally.
"""