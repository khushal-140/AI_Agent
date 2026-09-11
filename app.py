"""Flask web application for the AI Travel Agent."""

import os
import secrets

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from agent_executor import process_message
from memory import new_memory

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Server-side conversation store (per browser session). Memory and itineraries
# live here instead of the cookie so large plans cannot overflow the cookie.
SESSIONS = {}

MAX_MESSAGE_LENGTH = 1000


def _get_state() -> dict:
    """Get or create the server-side state for the current browser session."""
    session_id = session.get("sid")
    if not session_id:
        session_id = secrets.token_hex(16)
        session["sid"] = session_id
    return SESSIONS.setdefault(session_id, {"memory": new_memory(), "last_plan": None})


@app.route("/")
def index():
    """Homepage with the chat / planning interface."""
    return render_template("index.html")


@app.post("/chat")
def chat():
    """Handle one user message and return the agent's response as JSON."""
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"status": "error", "reply": "Please type your travel request first."}), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH]

    state = _get_state()
    try:
        result = process_message(state["memory"], message)
    except Exception:
        app.logger.exception("Agent failure")  # details go to the server log only
        return jsonify({
            "status": "error",
            "reply": "Something went wrong while planning your trip. Please try again.",
        }), 500

    if result.get("status") == "complete":
        state["last_plan"] = result

    return jsonify({
        "status": result.get("status"),
        "reply": result.get("reply"),
        "memory": state["memory"],
        "missing": result.get("missing", []),
        "tool_activity": result.get("tool_activity", []),
    })


@app.get("/itinerary")
def itinerary():
    """Full itinerary page for the latest completed plan."""
    state = _get_state()
    plan = state.get("last_plan")
    if not plan:
        return redirect(url_for("index"))
    return render_template(
        "result.html",
        itinerary=plan.get("itinerary", {}),
        tool_results=plan.get("tool_results", {}),
        memory=state["memory"],
    )


@app.post("/reset")
def reset():
    """Start a fresh conversation."""
    session_id = session.get("sid")
    if session_id:
        SESSIONS.pop(session_id, None)
    session.clear()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
