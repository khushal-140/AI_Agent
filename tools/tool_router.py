import json


from config import client, MODEL_NAME
from prompts import tool_selection_prompt


def select_tools(user_message):

    prompt = tool_selection_prompt(user_message)

    response = client.models.***REMOVED***(
        model=MODEL_NAME,
        contents=prompt
    )

    json_text = response.text.strip()

    if json_text.startswith("```json"):
        json_text = json_text.replace("```json", "", 1)

    if json_text.startswith("```"):
        json_text = json_text.replace("```", "", 1)

    if json_text.endswith("```"):
        json_text = json_text[:-3]

    json_text = json_text.strip()

    data = json.loads(json_text)

    return data["tools"]


