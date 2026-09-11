"""Gemini-powered tool routing.

The router decides WHICH tools a request needs (semantic understanding, not
keyword matching), and validates every name against the registry so a
hallucinated tool name can never reach the executor.
"""

from llm import ask_gemini_json
from prompts import followup_prompt, tool_selection_prompt
from tool_registry import TOOLS


def _validate_tool_names(raw) -> list:
    """Keep only valid, unique, registered tool names."""
    selected = []
    for name in raw if isinstance(raw, list) else []:
        if isinstance(name, str):
            name = name.strip().lower()
            if name in TOOLS and name not in selected:
                selected.append(name)
    return selected


def select_tools(user_message: str) -> list:
    """Ask Gemini which tools the message needs. Fails safe to no tools."""
    try:
        data = ask_gemini_json(tool_selection_prompt(user_message))
    except Exception:
        return []  # the plan is still generated without tool data
    tools = data.get("tools") if isinstance(data, dict) else None
    return _validate_tool_names(tools)


def decide_next_tools(user_message: str, tool_results: dict, executed: set) -> list:
    """Agent-loop observation step: are more tools needed?

    Never returns a tool that already ran, so the loop always terminates.
    """
    try:
        data = ask_gemini_json(followup_prompt(user_message, executed, tool_results))
    except Exception:
        return []  # stop the loop safely on any router failure
    tools = data.get("tools") if isinstance(data, dict) else None
    return [name for name in _validate_tool_names(tools) if name not in executed]
