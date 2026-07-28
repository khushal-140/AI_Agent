import requests

CITY_COORDINATES = {
    "goa": (15.2993, 74.1240),
    "manali": (32.2396, 77.1887),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "ahmedabad": (23.0225, 72.5714)
}

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light Drizzle",
    61: "Rain",
    71: "Snow",
    95: "Thunderstorm"
}

def get_weather(city):

    city = city.lower()

    if city not in CITY_COORDINATES:
        return "Weather not available."

    latitude, longitude = CITY_COORDINATES[city]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,weather_code"
    )

    response = requests.get(url, timeout=10)

    data = response.json()

    current = data["current"]
    
    code = current["weather_code"]

    description = WEATHER_CODES.get(
        code,
        "Unknown Weather"
    )

    return {
        "temperature": current["temperature_2m"],
        "description": description
    }
