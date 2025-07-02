import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Retrieve API Key from .env files
API_KEY = os.getenv("YELP_API_KEY")

# If the API key doesn't exist raise an error
if not API_KEY:
    raise ValueError("YELP_API_KEY not found in environment variables")


def get_attractions(city, num_days):
    """
    Gets the attraction spots(landmarks, parks and museums) based on the
    provide city

    Args:
      city (string): The city the user would like to visit
      num_days (int): The amount of days that would be spent on the visit

    Returns:
      list: Containing all the places of attraction that would exist in the area sorted by rating
      or None if an error occurs
    """

    # Yelp API call
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Custom request based on the city and
    # number of days for visit or more to give ai more choice
    limit = max(num_days * 2, 10)

    params = {
        "location": city,
        "categories": "landmarks, parks, museums",
        "limit": limit,
        "sort_by": "rating",
    }

    try:
        # Process the response into readable JSON format
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Yelp API: {e}")
        return None

    data = response.json()

    # Loop through the data and 
    # create a structured list from the given data from API response
    places = []
    for business in data.get("businesses", []):
        places.append(
            {
                "name": business["name"],
                "address": ", ".join(business["location"]["display_address"]),
                "rating": business["rating"],
                "url": business["url"],
            }
        )

    # Return the structred list
    return places
