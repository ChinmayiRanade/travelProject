import os
from openai import OpenAI
from dotenv import load_dotenv
from weather import get_weather_forecast  # Your own weather function/module

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_itinerary(destination, num_days, interest, attractions, budget):
    """
    Generates a travel itinerary using a generative AI model with weather integration.

    Args:
        destination (str): The travel destination.
        num_days (int): The number of days of the trip.
        interest (str): The user's interest focus.
        attractions (list): List of attractions with name, address, and rating.
        budget (int): Daily budget.

    Returns:
        str: AI-generated travel itinerary.
    """

    # Format the attractions info into a string
    names = []
    for p in attractions:
        line = f"- {p['name']} ({p['address']}, Rating: {p['rating']})"
        names.append(line)
    attractions_list = "\n".join(names)

    # Get weather forecast, handle exceptions gracefully
    try:
        weather_forecast = get_weather_forecast(destination, num_days)
        print(f"Weather forecast retrieved for {destination}")
    except Exception as e:
        print(f"Weather forecast failed: {e}")
        weather_forecast = "Weather forecast unavailable"

    # Compose the prompt to send to OpenAI
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

    # Call OpenAI's chat completion endpoint
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful travel planner. Your tone is concise, warm, and culturally aware. "
                        "Always consider weather conditions when making recommendations and provide practical advice."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"AI generation failed: {e}")
        return "Itinerary could not be generated due to an error."

# Example usage:
if __name__ == "__main__":
    sample_attractions = [
        {"name": "The Art Museum", "address": "123 Museum Rd", "rating": 4.7},
        {"name": "Central Park", "address": "Park Ave", "rating": 4.5},
        {"name": "City Aquarium", "address": "456 Ocean St", "rating": 4.6},
    ]

    itinerary = get_itinerary(
        destination="New York City",
        num_days=3,
        interest="art and nature",
        attractions=sample_attractions,
        budget=150
    )
    print(itinerary)
