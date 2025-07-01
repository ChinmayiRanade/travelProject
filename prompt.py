import os 
from google import genai
from google.genai import types
from apiYelp import get_attractions

# Set environment variables
my_api_key = os.getenv('GENAI_KEY')

genai.api_key = my_api_key
# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)


# WRITE YOUR CODE HERE

destination = input("Enter a city for your travel itinerary: ")
days = input("How many days are you traveling for? ")


attractions = get_attractions(destination)

print('\n Top attractions from Yelp: ')

for i, name in enumerate(attractions, 1):
  print(f'{i}. {name}')

print('\n')


names = []

for name in attractions:
  line = f"- {name}"
  names.append(line)

attractions_list = "\n".join(names)
  
  
prompt = (
  f"You are a travel assistant. Based on the following top places in {destination}:\n"
    f"{attractions_list}\n\n"
    f"Create a {days}-day travel itinerary that includes these attractions. "
    f"Each day's plan should be 3–4 sentences long, combining activities and meals. "
    f"Avoid overly long descriptions. Be friendly and informative, but keep it tight."
)
  
response = client.models.generate_content(
  model="gemini-2.5-flash",
  config=types.GenerateContentConfig(
    system_instruction="You are a helpful travel planner",
  ),
  contents=prompt,
)

print("Generated itinerary: ")
print(response.text)