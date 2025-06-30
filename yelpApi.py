import os
import requests

API_KEY = os.getenv("YELP_API_KEY")


def get_attractions(city):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    params = {
      "location": city,
      "term": "landmarks",
      "limit": 3
    }

    response = requests.get(url=url, headers=headers, params=params)
    data = response.json()

    for business in data["businesses"]:
      print(business["name"])

get_attractions("paris")