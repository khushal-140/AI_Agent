import json

from config import client, MODEL_NAME
from prompts import extraction_prompt, create_travel_prompt
from memory import memory
from conversation import ask_missing_information
from tools.weather import get_weather
from tools.tool_router import select_tools



def run_travel_agent():

    print("=" * 40)
    print("      AI TRAVEL AGENT")
    print("=" * 40)

    print("\nAI : Welcome to AI Travel Agent!\n")

    user_message = input("Describe your trip: ")

    prompt = extraction_prompt(user_message)

    response = client.models.***REMOVED***(
        model=MODEL_NAME,
        contents=prompt
    )

    # Gemini sometimes returns ```json ... ```
    json_text = response.text.strip()

    if json_text.startswith("```json"):
        json_text = json_text.replace("```json", "", 1)

    if json_text.startswith("```"):
        json_text = json_text.replace("```", "", 1)

    if json_text.endswith("```"):
        json_text = json_text[:-3]

    json_text = json_text.strip()

    travel_data = json.loads(json_text)

    for key, value in travel_data.items():
        if value is not None:
            memory[key] = value

    ask_missing_information()

    weather = get_weather(memory["destination"])
    
    final_prompt = create_travel_prompt(memory,weather)
    
    

    final_response = client.models.***REMOVED***(
        model=MODEL_NAME,
        contents=final_prompt
    )

    print("\n" + "=" * 50)
    print("      YOUR AI TRAVEL PLAN")
    print("=" * 50)

    print(final_response.text)
    



from tools.tool_router import select_tools

while True:

    message = input("You : ")

    if message.lower() == "exit":
        break

    tools = select_tools(message)

    print("\nSelected Tools")
    print(tools)