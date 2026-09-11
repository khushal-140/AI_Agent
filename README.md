# AI Travel Agent ✈️

**Plan smarter. Travel better.**

An AI-agent-style travel planning application built with Python and Google's
Gemini API. It is **not** a simple chatbot: it has conversation memory,
natural-language understanding, semantic tool selection, a generic tool
registry + executor, an agent loop, real external APIs, and a professional
Flask web interface.

Tell it what you want in plain language:

> *"I am Khushal and I want to visit Goa for 5 days with two friends. My budget
> is ₹25,000 and I want to travel by train."*

The agent extracts your trip details into memory, asks you **only** for the
information that is still missing, calls the tools it needs (live weather,
budget math, hotels, maps, currency), and generates a personalized day-by-day
itinerary with budget breakdown, hotel suggestions, food recommendations and
travel tips.

---

## Features

- 🧠 **Conversation memory** — extracts name, destination, days, budget,
  travelers and transport from natural language; never asks twice for
  something you already said; never overwrites known details with `null`.
- 🔎 **LLM information extraction** — Gemini returns structured JSON (with
  markdown code-fence handling and validation).
- 🧰 **Tool registry + generic executor** — six tools described with metadata
  (name, description, function, typed parameters). The executor reads the
  metadata, pulls parameter values from memory, converts types and runs the
  tool — no `if tool == "weather":` chains anywhere.
- 🤖 **Semantic tool selection** — Gemini decides which tools are needed
  ("Should I carry an umbrella?" → `weather`), and every returned tool name is
  validated against the registry.
- 🔁 **Agent loop** — reason → select tools → execute → observe → decide
  whether more tools are needed → repeat, capped at `MAX_ITERATIONS = 5`.
- 🌐 **Professional Flask web UI** — travel-themed, responsive, animated chat
  interface with live trip-details sidebar and tool-activity indicators, plus
  a full itinerary page.
- 🛡️ **Robust error handling** — API failures, invalid JSON, invalid budgets,
  zero travelers, unknown tools, missing parameters and network timeouts all
  fail safely with meaningful messages. The API key never leaves `.env`.

## Technologies

| Layer      | Technology                                    |
| ---------- | ***REMOVED***--------------------- |
| Language   | Python 3.x                                     |
| LLM        | Google Gemini (`google-genai` SDK)             |
| Web        | Flask + HTML5 + CSS3 + JavaScript              |
| APIs       | Open-Meteo (weather + geocoding), open.er-api.com (exchange rates) |
| Config     | python-dotenv, JSON                            |

## Architecture

```
User
 ↓
Natural-language input
 ↓
Gemini → Information extraction (structured JSON)
 ↓
Conversation memory (never loses known details)
 ↓
Tool selection (Gemini, validated against registry)
 ↓
Tool Registry → Tool Execution (generic executor)
 ↓
Tool results (live / calculated / demo, always labeled)
 ↓
Gemini → Personalized travel plan
 ↓
User
```

The agent loop in `agent_executor.py` repeats *select → execute → observe →
decide* up to `MAX_ITERATIONS = 5` times, then stops safely.

## Folder structure

```
AI_Agent/
├── app.py               # Flask web application
├── main.py              # CLI entry point
├── travel_agent.py      # CLI chat loop
├── config.py            # .env loading + single shared Gemini client + model name
├── llm.py               # All Gemini calls (JSON mode, code-fence handling)
├── prompts.py           # Every prompt template in one place
├── memory.py            # Trip memory: merge rules + type normalization
├── conversation.py      # Extraction, missing-field questions (CLI + web)
├── tool_router.py       # Gemini tool selection + agent-loop follow-up decision
├── tool_registry.py     # Metadata registry for all tools
├── agent_executor.py    # Generic executor + agent loop + final pipeline
├── requirements.txt
├── .env                 # ***REMOVED*** (never committed)
├── tools/
│   ├── budget.py        # Budget split + category breakdown (calculated)
│   ├── weather.py       # Live weather via Open-Meteo
│   ├── hotel.py         # Hotel interface, mock provider (labeled demo)
│   ├── flight.py        # Flight interface, mock provider (labeled demo)
│   ├── maps.py          # Live geocoding + demo attractions dataset
│   └── currency.py      # Live exchange rates via open.er-api.com
├── templates/
│   ├── index.html       # Chat / planning interface
│   └── result.html      # Full itinerary page
└── static/
    ├── css/style.css
    └── js/script.js
```

## Installation

```bash
# 1. Clone / copy the project
# 2. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root:

```
***REMOVED***=your_gemini_api_key_here
```

- Get a free key at https://aistudio.google.com/apikey
- `GEMINI_MODEL` (optional) overrides the model name (default:
  `gemini-3.***REMOVED***`).
- **Never commit `.env`** — it is already listed in `.gitignore`.

## How to run

Web app (recommended):

```bash
python app.py
# open http://127.0.0.1:5000
```

Command-line version:

```bash
python main.py
```

## Example conversation

```
You: I want to visit Goa for 4 days with a budget of ₹30,000.
AI:  Great choice! Goa for 4 days with a ₹30,000 budget sounds wonderful.
     How many travelers are going?

You: We are 4 people, traveling by flight from Mumbai. I'm Khushal.
AI:  Your personalized travel plan is ready! ✈️
     [ Trip details sidebar fills in ]
     [ Weather 🌤️, Budget 💰, Hotels 🏨 tools run ]
     → "View Full Itinerary" opens the complete day-by-day plan
```

The plan includes: trip summary, day-by-day plan (morning/afternoon/evening),
estimated budget breakdown, weather (live), hotel suggestions (demo),
food recommendations and travel tips — with each section labeled by its
source (user-provided, live tool data, calculated, demo or AI estimate).

## Tool architecture

Each tool is a dict in `tool_registry.py`:

```python
WEATHER_TOOL = {
    "name": "weather",
    "description": "Gets current weather and a short forecast for a destination (live data).",
    "function": get_weather,
    "parameters": [{"name": "destination", "type": str}],
}
```

The executor is fully generic — for each selected tool it reads the metadata,
takes each parameter's value from conversation memory (or a declared
`default`), converts the type, validates it, and calls the function. Adding a
new tool = write the function + register it. Nothing else changes.

| Tool     | Data source                          | Label        |
| -------- | ***REMOVED***------------ | ------------ |
| weather  | Open-Meteo (geocoding + forecast)    | live         |
| budget   | Pure calculation                     | calculated   |
| hotel    | Mock provider (deterministic)        | demo         |
| flight   | Mock provider (fictional airlines)   | demo         |
| maps     | Open-Meteo geocoding + demo dataset  | live + demo  |
| currency | open.er-api.com                      | live         |

Mock tools are **always** clearly labeled as demo data — the app never
presents mock hotel/flight results as real.

## Security notes

- The Gemini API key lives only in `.env` and is never hardcoded or exposed
  in error messages.
- Tool names returned by Gemini are validated against the registry before
  execution; parameters are converted and validated before any call.
- User input is length-limited and never executed as code.

## Future improvements

- Live hotel/flight search via Amadeus, Skyscanner or Booking.com APIs.
- Let the router return tool *arguments* (e.g. arbitrary currency pairs) in
  addition to tool names.
- Persistent memory in a database instead of per-session storage.
- Multi-city trips and real-day itinerary dates.
- Streaming responses in the chat UI.
