from memory import memory


def get_missing_fields():
    missing = []

    for key, value in memory.items():
        if value is None:
            missing.append(key)

    return missing


def ask_missing_information():

    if memory["name"] is None:
        memory["name"] = input("AI : What is your name? : ")

    if memory["destination"] is None:
        memory["destination"] = input("AI : Which place do you want to visit? : ")

    if memory["days"] is None:
        memory["days"] = input("AI : How many days? : ")

    if memory["budget"] is None:
        memory["budget"] = input("AI : What is your budget (₹)? : ")

    if memory["travelers"] is None:
        memory["travelers"] = input("AI : How many travelers? : ")

    if memory["transport"] is None:
        memory["transport"] = input("AI : Preferred transport? : ")