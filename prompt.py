import os 
from google import genai
from google.genai import types
from apiYelp import get_attractions

my_api_key = os.getenv('GENAI_KEY')
genai.api_key = my_api_key


client = genai.Client(api_key=my_api_key)

def generate_itinerary(destination, days, attractions):
    print('\n📍 Top attractions from Yelp:\n')
    for i, place in enumerate(attractions, 1):
        print(f"{i}. {place['name']}")
        print(f"   📍 Address: {place['address']}")
        print(f"   ⭐ Rating: {place['rating']}")
        print(f"   🔗 More info: {place['url']}\n")

    names = []
    for place in attractions:
        line = f"- {place['name']} ({place['address']}, Rating: {place['rating']})"
        names.append(line)

    attractions_list = "\n".join(names)

    prompt = (
        f"You are a professional travel assistant. The user is visiting {destination} for the first time.\n"
        f"Based on the following top-rated attractions:\n"
        f"{attractions_list}\n\n"
        f"Create a detailed {days}-day travel itinerary. For each day:\n"
        f"- Include a clear morning, afternoon, and evening plan.\n"
        f"- Specify which attraction to visit and when.\n"
        f"- Suggest a local meal (lunch or dinner) with cuisine type.\n"
        f"- Recommend relaxing or fun evening activities.\n"
        f"- Use one greeting or phrase in the city's local language.\n\n"
        f"Format the output with 'Day 1', 'Day 2', etc. Use concise but helpful instructions suitable for someone new to the city."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful travel planner. Your tone is concise, warm, and culturally aware.",
        ),
        contents=prompt,
    )

    print("\n🧳 Generated itinerary:")
    print(response.text)