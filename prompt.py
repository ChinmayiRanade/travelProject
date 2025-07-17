import os
import openai
from dotenv import load_dotenv
from weather import get_weather_forecast  # Import your weather function

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_itinerary(destination, num_days, interest, attractions, budget):
    """
    Generates a travel itinerary using a generative AI model with weather integration.
    Args:
        destination (str): The travel destination.
        num_days (int): The duration of trip.
        interest (str): The User's interests.
        attractions (list): A list of dictionaries of attractions to visit.
        budget (int): Daily budget for the trip.
    Returns:
        str: The generated itinerary text.
    """
    names = []
    for p in attractions:
        line = f"- {p['name']} ({p['address']}, Rating: {p['rating']})"
        names.append(line)
    attractions_list = "\n".join(names)
    
    # Get weather forecast for the destination
    weather_forecast = ""
    try:
        weather_forecast = get_weather_forecast(destination, num_days)
        print(f"Weather forecast retrieved for {destination}")
    except Exception as e:
        print(f"Weather forecast failed: {e}")
        weather_forecast = "Weather forecast unavailable"
    
    prompt = (
        f"You are a helpful and culturally aware travel planner. "
        f"The user is visiting {destination} for {num_days} days and is "
        f"particularly interested in {interest}.\n"
        f"They have a daily travel budget of ${budget}.\n\n"
        f"WEATHER FORECAST:\n{weather_forecast}\n\n"
        f"Here are the top attractions in the city:\n"
        f"{attractions_list}\n\n"
        f"Based on these locations, their interests, the ${budget} daily budget, "
        f"and the weather forecast above, create a detailed {num_days}-day travel itinerary. "
        f"Each day must include:\n"
        f"- 🌤️ Weather conditions for the day (from the forecast above)\n"
        f"- Morning, afternoon, and evening activity (with time suggestions)\n"
        f"- Weather-appropriate activity recommendations (indoor/outdoor based on conditions)\n"
        f"- Mention which attraction is visited and when\n"
        f"- Recommend a local meal (e.g., lunch/dinner) with cuisine type\n"
        f"- Suggest an evening experience\n"
        f"- Use one local-language greeting or phrase each day\n"
        f"- 💰 For each day, estimate how much the user might spend on: "
        f"attraction tickets, food, transport, and extras. "
        f"Make sure the total stays within ${budget}.\n"
        f"- 👕 Include clothing/packing suggestions based on weather\n\n"
        f"IMPORTANT: Use the weather information to:\n"
        f"- Recommend indoor attractions on rainy/cold days\n"
        f"- Suggest outdoor activities on sunny days\n"
        f"- Adjust timing based on weather conditions\n"
        f"- Include weather-specific tips (umbrella, sunscreen, etc.)\n\n"
        f"Use friendly tone, clear structure, and format the output with 'Day 1', 'Day 2', etc."
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful travel planner. Your tone is concise, warm, and culturally aware. "
                    "Always consider weather conditions when making recommendations and provide practical advice."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"AI generation failed: {e}")
        return "Itinerary could not be generated due to an error."