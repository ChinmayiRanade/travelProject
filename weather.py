import requests
import os
from datetime import datetime, timedelta

OWM_KEY = os.getenv("OPENWEATHER_API_KEY")
OWM_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather_forecast(city: str, days: int = 1) -> str:
    """
    Get weather forecast for a city for specified number of days.
    
    Args:
        city: City name
        days: Number of days to get forecast for (max 5)
    
    Returns:
        Formatted weather forecast string
    """
    if days > 5:
        days = 5  # OpenWeatherMap free tier only gives 5 days
    
    params = {
        "q": city,
        "appid": OWM_KEY,
        "units": "imperial",
        "cnt": days * 8  # 8 forecasts per day (every 3 hours)
    }
    
    response = requests.get(OWM_FORECAST_ENDPOINT, params=params, timeout=10)
    
    if response.status_code != 200:
        return "Weather forecast unavailable"
    
    data = response.json()
    forecasts = data["list"]
    
    # Group forecasts by date
    daily_forecasts = {}
    
    for forecast in forecasts:
        # Convert timestamp to date
        date = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
        
        if date not in daily_forecasts:
            daily_forecasts[date] = []
        
        daily_forecasts[date].append({
            "time": datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M"),
            "description": forecast["weather"][0]["description"].capitalize(),
            "temp": round(forecast["main"]["temp"], 1),
            "feels_like": round(forecast["main"]["feels_like"], 1),
            "humidity": forecast["main"]["humidity"]
        })
    
    # Format output
    result = f"Weather forecast for {city}:\n\n"
    
    for i, (date, day_forecasts) in enumerate(list(daily_forecasts.items())[:days]):
        # Convert date to more readable format
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        readable_date = date_obj.strftime("%A, %B %d")
        
        result += f"Day {i+1} - {readable_date}:\n"
        
        # Get representative forecast (midday if available, otherwise first available)
        midday_forecast = None
        for f in day_forecasts:
            if "12:00" in f["time"] or "15:00" in f["time"]:
                midday_forecast = f
                break
        
        if not midday_forecast:
            midday_forecast = day_forecasts[0]
        
        result += f"  {midday_forecast['description']}, {midday_forecast['temp']}°F (feels like {midday_forecast['feels_like']}°F)\n"
        result += f"  Humidity: {midday_forecast['humidity']}%\n\n"
    
    return result.strip()

def get_current_weather(city: str) -> str:
    """
    Get current weather for a city.
    """
    OWM_CURRENT_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": OWM_KEY,
        "units": "imperial"
    }
    
    response = requests.get(OWM_CURRENT_ENDPOINT, params=params, timeout=10)
    
    if response.status_code != 200:
        return "Weather unavailable"
    
    data = response.json()
    desc = data["weather"][0]["description"].capitalize()
    temp = round(data["main"]["temp"], 1)
    return f"{desc}, {temp}°F"

def get_user_input():
    """
    Get user input for city and number of days.
    """
    print("=== Travel Weather Assistant ===")
    
    while True:
        city = input("\nEnter the city you're visiting: ").strip()
        if city:
            break
        print("Please enter a valid city name.")
    
    while True:
        try:
            days = int(input("How many days will you be there? (1-5): ").strip())
            if 1 <= days <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    return city, days

# Example usage
if __name__ == "__main__":
    # Check if API key is available
    if not OWM_KEY:
        print("Error: Please set your OPENWEATHER_API_KEY environment variable.")
        print("You can get a free API key at: https://openweathermap.org/api")
        exit()
    
    try:
        # Get user input
        city, days = get_user_input()
        
        print(f"\nFetching weather for {city} for {days} day(s)...\n")
        
        if days == 1:
            # For 1 day, show current weather
            print("Current weather:")
            current_weather = get_current_weather(city)
            print(current_weather)
        else:
            # For multiple days, show forecast
            forecast = get_weather_forecast(city, days)
            print(forecast)
            
    except KeyboardInterrupt:
        print("\n\nGoodbye! Have a great trip!")
    except Exception as e:
        print(f"An error occurred: {e}")