import os
import openai
from weather import get_weather_forecast  # your existing weather import

# Set up OpenAI client using the new SDK style
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_itinerary(destination, num_days, interest, attractions, budget):
    names = []
    for p in attractions:
        line = f"- {p['name']} ({p['address']}, Rating: {p['rating']})"
        names.append(line)
    attractions_list = "\n".join(names)

    # Weather
    try:
        weather_forecast = get_weather_forecast(destination, num_days)
    except Exception as e:
        print(f"Weather error: {e}")
        weather_forecast = "Weather forecast unavailable."

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
        f"- 🌤️ Weather conditions\n"
        f"- Morning, afternoon, and evening activity (with time suggestions)\n"
        f"- Attraction visited and when\n"
        f"- Local meal recommendation\n"
        f"- Local-language greeting or phrase\n"
        f"- Daily budget breakdown\n"
        f"- Clothing/packing tips\n"
        f"- Weather-specific suggestions (umbrella, sunscreen, etc.)\n\n"
        f"Format using 'Day 1', 'Day 2', etc. Keep it clear and friendly."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you're using a cheaper option
            messages=[
                {"role": "system", "content": "You are a concise, culturally aware travel planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI generation failed: {e}")
        return "Itinerary could not be generated."
