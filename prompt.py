import os 
from google import genai
from google.genai import types

# Set environment variables
my_api_key = os.getenv('GENAI_KEY')

genai.api_key = my_api_key
# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)


# WRITE YOUR CODE HERE
def ai_generate_itinerary():
  destination = input("Enter a city for your travel itinerary: ")
  days = input("How many days are you traveling for? ")

  
  
  prompt = (
    f"Create a {days}-day itinerary for {destination}",
  )
  
  response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="You are a university instructor and can explain programming concepts clearly in a few words."
    ),
    contents=prompt,
  )