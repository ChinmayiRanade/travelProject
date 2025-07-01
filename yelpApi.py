import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# Retrieve API Key from .env files
API_KEY = os.getenv("YELP_API_KEY")

# If the API key doesn't exist raise an error
if not API_KEY:
    raise ValueError("YELP_API_KEY not found in environment variables")


def get_attractions(city, num_days):
    """
    Gets the attraction spots(landmarks, parks and museums) based on the provide city

    Args:
      city (string): The city the user would like to visit
      num_days (int): The amount of days that would be spent on the visit 
    
    Returns:
      list: Containing all the places of attraction that would exist in the area sorted by rating
    """

    # Yelp API call
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Custom request based on the city and number of days for visit
    params = {
      "location": city,
      "categories": "landmarks, parks, museums",
      "limit": num_days,
      'sort_by': 'rating',
    }

    # Process the response into readable JSON format
    response = requests.get(url=url, headers=headers, params=params)
    data = response.json()

    # Loop through the data and create a structured list from the given data from API response
    places = []
    for business in data.get('businesses', []):
        places.append({
            'name': business['name'],
            'address': ", ".join(business['location']['display_address']),
            'rating': business['rating'],
            'url': business['url']
        })

    # Return the structred list
    return places

# CLI user input to get the city and number of days for the visit
destination = input("Where do you want to visit? ")
num_days = int(input("How many days will you be staying? "))

itinerary = get_attractions(destination, num_days)

# CLI printed format of the results
print("\nYour Itinerary:")
for i, place in enumerate(itinerary, 1):
    print(f"Day {i}: {place['name']} ({place['rating']}★) - {place['address']}")
    print(f"More info: {place['url']}\n")

# Dumps the data into a JSON file
with open("itinerary.json", "w") as f:
    json.dump(itinerary, f, indent=4)
print("\n Itinerary saved to itinerary.json")