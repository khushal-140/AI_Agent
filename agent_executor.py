"""Agent executor and agent loop for the AI Travel Agent.

The executor is GENERIC: it reads each tool's metadata from the registry
(function, parameters, types), pulls parameter values from conversation
memory, converts and validates types, then executes. Adding a new tool never
requires changes here.

The agent loop follows: reason -> select tools -> execute -> observe ->
decide whether more tools are needed -> repeat -> final answer, capped at
MAX_ITERATIONS so it can never run forever.
"""

from conversation import extract_information, generate_missing_question, get_missing_fields
from llm import ask_gemini, ask_gemini_json
from memory import update_memory
from prompts import create_travel_prompt, travel_text_prompt
from tool_registry import TOOLS
from tool_router import decide_next_tools, select_tools

MAX_ITERATIONS = 5


def execute_tool(tool_name: str, memory: dict) -> dict:
    """Run one registered tool after validating and converting parameters."""
    tool = TOOLS.get(tool_name)
    if tool is None:
        return {"status": "error", "error": f"Unknown tool '{tool_name}'."}

    kwargs = {}
    for spec in tool.get("parameters", []):
        value = memory.get(spec.get("memory_key", spec["name"]))
        if value in (None, ""):
            value = spec.get("default")
        if value in (None, ""):
            return {
                "status": "error",
                "error": f"Missing required value '{spec['name']}' for the {tool_name} tool.",
            }
        try:
            value = spec["type"](value)
        except (TypeError, ValueError):
            return {
                "status": "error",
                "error": f"Invalid value for '{spec['name']}': {value!r}.",
            }
        kwargs[spec["name"]] = value

    try:
        return tool["function"](**kwargs)
    except Exception as exc:  # safety net: tools handle their own errors too
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}


def run_agent(memory: dict, user_message: str) -> dict:
    """The agent loop: select tools, execute, observe, decide, repeat."""
    tool_results: dict = {}
    activity: list = []
    executed: set = set()

    selected = select_tools(user_message)
    for _ in range(MAX_ITERATIONS):
        if not selected:
            break
        for tool_name in selected:
            if tool_name in executed:
                continue  # never run the same tool twice in one request
            executed.add(tool_name)
            result = execute_tool(tool_name, memory)
            tool_results[tool_name] = result
            activity.append({
                "tool": tool_name,
                "status": result.get("status", "error"),
                "error": result.get("error"),
            })
        selected = decide_next_tools(user_message, tool_results, executed)

    return {"tool_results": tool_results, "activity": activity, "iterations": len(executed)}


def generate_itinerary(user_message: str, memory: dict, tool_results: dict) -> dict:
    """Turn memory + tool results into a structured itinerary.

    JSON mode first; if that fails, a plain-text plan so the user always
    gets a useful answer.
    """
    try:
        data = ask_gemini_json(create_travel_prompt(user_message, memory, tool_results))
        if isinstance(data, dict) and data.get("days"):
            data.setdefault("chat_reply", "Your personalized travel plan is ready! ✈️")
            return data
    except Exception:
        pass

    try:
        text = ask_gemini(travel_text_prompt(user_message, memory, tool_results))
        return {"chat_reply": "Your travel plan is ready! ✈️", "raw": True, "raw_text": text}
    except Exception:
        return {
            "chat_reply": "I could not build the full itinerary right now. Please try again in a moment.",
            "raw": True,
            "raw_text": "",
            "error": True,
        }


def plan_trip(memory: dict, user_message: str) -> dict:
    """Run the tools and generate the final plan (memory must be complete)."""
    agent_result = run_agent(memory, user_message)
    itinerary = generate_itinerary(user_message, memory, agent_result["tool_results"])
    return {
        "status": "complete",
        "reply": itinerary.get("chat_reply", "Your travel plan is ready!"),
        "tool_activity": agent_result["activity"],
        "tool_results": agent_result["tool_results"],
        "itinerary": itinerary,
    }


def process_message(memory: dict, user_message: str) -> dict:
    """Full agent pipeline for one user message (shared by CLI and web app).

    1. Extract trip details from the message (Gemini, structured JSON)
    2. Merge them into conversation memory (never overwriting with None)
    3. If details are missing, ask ONLY for what is missing
    4. Otherwise run the agent loop and generate the final plan
    """
    user_message = (user_message or "").strip()
    if not user_message:
        return {"status": "error", "reply": "Please type your travel request first."}

    extracted = extract_information(user_message)
    update_memory(memory, extracted)

    missing = get_missing_fields(memory)
    if missing:
        return {
            "status": "need_info",
            "reply": generate_missing_question(user_message, memory, missing),
            "missing": missing,
        }

    return plan_trip(memory, user_message)
