import requests
import os
from dotenv import load_dotenv
load_dotenv()

OWM_KEY = os.getenv("OPENWEATHER_API_KEY")

if not OWM_KEY:
    raise KeyError("Weather API Key not provided")

OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city: str) -> str:
    params = {
        "q": city,
        "appid": OWM_KEY,
        "units": "imperial"}
    
    response = requests.get(OWM_ENDPOINT, params=params, timeout=10)

    if response.status_code != 200:
        return "Weather unavailable"
    


    data = response.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"], 1)
    return f"{desc}, {temp}°F"

print(get_weather("Lisbon"))