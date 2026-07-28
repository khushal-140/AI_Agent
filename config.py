from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("***REMOVED***")
)

MODEL_NAME ="gemini-3.***REMOVED***"