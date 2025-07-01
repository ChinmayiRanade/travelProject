import os 
from google import genai
from google.genai import types
from apiYelp import get_attractions
from db import save_attractions

my_api_key = os.getenv('GENAI_KEY')
genai.api_key = my_api_key


client = genai.Client(api_key=my_api_key)

destination = input("Enter a city for your travel itinerary: ")
days = input("How many days are you traveling for? ")


attractions = get_attractions(destination, int(days))

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
    f"You are a travel assistant. Based on the following top places in {destination}:\n"
    f"{attractions_list}\n\n"
    f"Create a {days}-day travel itinerary that includes these attractions. "
    f"Each day's plan should be 4–5 sentences long, combining activities and meals. "
    f"Avoid overly long descriptions. Be friendly and informative, but keep it tight. "
    f"Include one phrase or greeting in the local language per day."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful travel planner. Your tone is concise, warm, and culturally aware.",
    ),
    contents=prompt,
)

print("\nGenerated itinerary:")
print(response.text)
