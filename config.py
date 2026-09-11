"""Central configuration for the AI Travel Agent.

Loads environment variables and creates the single shared Gemini client.
Never create additional Gemini clients in other modules - import from here.
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

***REMOVED*** = os.getenv("***REMOVED***")
if not ***REMOVED***:
    raise RuntimeError(
        "***REMOVED*** is not set. Create a .env file containing "
        "***REMOVED***=your_key (see README.md for details)."
    )

# One shared client for the whole application.
client = genai.Client(api_key=***REMOVED***)

# Single place to change the Gemini model.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.***REMOVED***")

# HTTP timeout (seconds) used by every external API call.
API_TIMEOUT = 10
