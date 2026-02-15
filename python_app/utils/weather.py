import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

def get_weather(lat: float, lon: float):
    """
    Fetches current weather data for the given coordinates.
    Returns a dict with condition, description, temp, and is_raining boolean.
    """
    if not OPENWEATHER_API_KEY:
        return {
            "condition": "Clear",
            "description": "Clear sky (Mock)",
            "temp": 25.0,
            "is_raining": False
        }

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        condition = data['weather'][0]['main']
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        
        is_raining = condition in ['Rain', 'Drizzle', 'Thunderstorm']

        return {
            "condition": condition,
            "description": description,
            "temp": temp,
            "is_raining": is_raining
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {
            "condition": "Unknown",
            "description": "Unavailable",
            "temp": 20.0,
            "is_raining": False
        }
