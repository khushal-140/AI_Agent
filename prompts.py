"""All Gemini prompt templates used by the AI Travel Agent.

Keeping prompts in one place makes them easy to review and improve without
touching application logic. The tool catalog is built dynamically from the
registry, so adding a new tool automatically updates the router prompts.
"""

import json

from tool_registry import TOOLS


def _tool_catalog() -> str:
    """Human-readable list of registered tools for the prompts."""
    lines = []
    for index, tool in enumerate(TOOLS.values(), start=1):
        lines.append(f"{index}. {tool['name']} - {tool['description']}")
    return "\n".join(lines)


def extraction_prompt(user_message: str) -> str:
    """Prompt that turns a natural-language message into structured JSON."""
    return f"""You are an information-extraction engine for a travel planning app.

Extract travel details from the user's message.

Return ONLY valid JSON with exactly these keys (use null for anything not mentioned):
{{
    "name": null,
    "destination": null,
    "days": null,
    "budget": null,
    "travelers": null,
    "transport": null,
    "origin": null
}}

Rules:
- "days" and "travelers" must be integers.
- "travelers" is the total number of people travelling, including the user.
  ("me and two friends" means 3 travelers.)
- "budget" must be a plain number in rupees. Remove currency symbols, commas
  and words (e.g. "Rs 30,000" -> 30000, "1.5 lakh" -> 150000).
- "transport" must be one of: flight, train, bus, car, any.
- "origin" is the departure city if the user mentions one (e.g. "from Mumbai").
- If a field is not mentioned in THIS message, leave it as null.
- Do not invent information. Do not add extra keys.

User message: {user_message}
"""


def tool_selection_prompt(user_message: str) -> str:
    """Prompt that asks Gemini which registered tools the message needs."""
    return f"""You are the tool router of an AI travel agent.

Available tools:
{_tool_catalog()}

Decide which tools are needed to answer the user's message.

Rules:
- Understand the MEANING of the request, not just keywords.
  Example: "Should I carry an umbrella?" needs the weather tool.
- Select "flight" only if the user's departure/origin city is known.
- Select "hotel" when accommodation is relevant to the request.
- If no tool is needed, return an empty list.
- Return only tool names from the available list.

Return ONLY valid JSON in this format:

{{
    "tools": ["weather", "budget"]
}}

User message: {user_message}
"""


def followup_prompt(user_message: str, executed_tools, tool_results: dict) -> str:
    """Agent-loop observation step: does the agent need more tools?"""
    summary = {}
    for name, result in tool_results.items():
        summary[name] = result.get("status", "error")
    summary_text = json.dumps(summary, indent=2)[:1500]

    return f"""You are the agent-loop controller of an AI travel agent.

The user request was: "{user_message}"

Tools already executed (never select these again):
{", ".join(executed_tools) if executed_tools else "none"}

Their result statuses:
{summary_text}

Available tools:
{_tool_catalog()}

Decide whether one or more ADDITIONAL tools are needed to fully answer the
user's request. If the information already collected is enough, return an
empty list.

Return ONLY valid JSON in this format:

{{
    "tools": []
}}
"""


def missing_info_prompt(user_message: str, memory: dict, missing_fields) -> str:
    """Prompt that phrases a friendly question asking ONLY for missing details."""
    known = {key: value for key, value in memory.items() if value not in (None, "")}
    known_text = json.dumps(known) if known else "nothing yet"

    return f"""You are a friendly AI travel agent chatting with a user.

Details already collected: {known_text}

The user just said: "{user_message}"

Still missing: {", ".join(missing_fields)}.

Write ONE short, warm message (max 3 sentences) that acknowledges what the
user said and asks ONLY for the missing details. Never ask again for details
that are already known. If nothing is known yet, greet them briefly and ask
for the missing details in a natural, conversational way.

Return ONLY the message text. No JSON, no markdown, no lists.
"""


def create_travel_prompt(user_message: str, memory: dict, tool_results: dict, json_mode: bool = True) -> str:
    """Prompt that generates the final personalized travel plan."""
    results_text = json.dumps(tool_results, indent=2, default=str)
    days = memory.get("days") or 3

    json_instructions = ""
    if json_mode:
        json_instructions = """
Return ONLY valid JSON matching exactly this schema:

{
    "chat_reply": "one friendly sentence telling the user the plan is ready",
    "trip_summary": "2-3 sentence overview of the trip",
    "days": [
        {
            "day": 1,
            "title": "short title for the day",
            "morning": "morning plan",
            "afternoon": "afternoon plan",
            "evening": "evening plan"
        }
    ],
    "budget_breakdown": {
        "transportation": 0,
        "hotel": 0,
        "food": 0,
        "activities": 0,
        "miscellaneous": 0,
        "total": 0
    },
    "food_recommendations": ["local dishes and where to try them"],
    "travel_tips": ["practical tips"]
}
"""

    return f"""You are an expert travel planner creating a personalized plan.

Traveler details (provided by the user):
- Name: {memory.get("name")}
- Destination: {memory.get("destination")}
- Days: {days}
- Total budget: Rs {memory.get("budget")}
- Travelers: {memory.get("travelers")}
- Preferred transport: {memory.get("transport")}
- Original request: "{user_message}"

Tool results (live/demo data retrieved by the agent's tools):
{results_text}

Rules:
- Create exactly {days} day entries in "days".
- Weather facts MUST come only from the weather tool result above. If no
  weather result exists, say nothing about current weather.
- Hotel suggestions MUST come only from the hotel tool result above.
- Budget numbers are ESTIMATES in rupees and should fit within the user's
  total budget; "total" must equal the sum of the categories.
- The app renders weather, hotels and the budget tool figures itself - do not
  repeat live weather/hotel data inside the JSON sections above.
- Write in clear, simple English.
{json_instructions}
"""


def travel_text_prompt(user_message: str, memory: dict, tool_results: dict) -> str:
    """Fallback prompt returning a plain-text plan if JSON mode fails."""
    base = create_travel_prompt(user_message, memory, tool_results, json_mode=False)
    return base + """
Write the plan as clean text with these sections:
1. Trip Summary
2. Day-wise Itinerary (Morning / Afternoon / Evening for each day)
3. Estimated Expenses
4. Hotel Suggestions
5. Food Recommendations
6. Travel Tips

Clearly mark which numbers are estimates. Do not invent live weather data.
"""
