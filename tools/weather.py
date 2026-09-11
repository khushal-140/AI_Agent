"""Weather tool: live weather via the free Open-Meteo API (no key needed)."""

import requests

from config import API_TIMEOUT
from tools.geocoding import get_coordinates

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def _condition(code):
    """Translate an Open-Meteo WMO weather code into readable text."""
    return WEATHER_CODES.get(code, "Unknown")


def get_weather(destination: str) -> dict:
    """Return current weather and a short forecast for the destination."""
    if not destination or not str(destination).strip():
        return {"status": "error", "error": "Destination is required for weather lookup."}

    place = get_coordinates(str(destination).strip())
    if place is None:
        return {"status": "error", "error": f"Could not find coordinates for '{destination}'."}

    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Weather service timed out. Please try again."}
    except requests.exceptions.RequestException:
        return {"status": "error", "error": "Weather service is currently unavailable."}
    except (KeyError, ValueError):
        return {"status": "error", "error": "Weather service returned unexpected data."}

    current = data.get("current", {})
    daily = data.get("daily", {})
    dates = daily.get("time", []) or []
    max_temps = daily.get("temperature_2m_max") or [None] * len(dates)
    min_temps = daily.get("temperature_2m_min") or [None] * len(dates)
    codes = daily.get("weather_code") or [None] * len(dates)
    rain = daily.get("precipitation_probability_max") or [None] * len(dates)

    return {
        "status": "success",
        "source": "Open-Meteo (live)",
        "destination": place.get("name"),
        "country": place.get("country"),
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "condition": _condition(current.get("weather_code")),
        "humidity": current.get("relative_humidity_2m"),
        "wind_kph": current.get("wind_speed_10m"),
        "forecast": [
            {
                "date": dates[index],
                "max": max_temps[index],
                "min": min_temps[index],
                "condition": _condition(codes[index]),
                "rain_chance": rain[index],
            }
            for index in range(len(dates))
        ],
    }
