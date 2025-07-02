import os
import google.generativeai as genai
from yelpApi import get_attractions

genai.configure(api_key=os.getenv("GENAI_KEY"))


def get_itinerary(destination, num_days, interest, attractions):
    """
    Generates a travel itinerary using a generative AI model.

    Args:
        destination (str): The travel destination.
        num_days (int): The duration of trip.
        interest (str): The User's intersts.
        attractions (list): A list of dictionaries of attractions to visit.

    Returns:
        str: The generated itinerary text.
    """
    # attractions = get_attractions(destination, num_days)


    # print("\n📍 Top attractions from Yelp:\n")

    # for i, place in enumerate(attractions, 1):
    #     print(f"{i}. {place['name']}")
    #     print(f"   📍 Address: {place['address']}")
    #     print(f"   ⭐ Rating: {place['rating']}")
    #     print(f"   🔗 More info: {place['url']}\n")
    
    # Create a formatted string of attractions for the prompt
    names = []
    for place in attractions:
        line = f"- {place['name']} ({place['address']}, Rating: {place['rating']})"
        names.append(line)

    attractions_list = "\n".join(names)

    prompt = (
        f"You are a helpful and culturally aware travel planner. "
        f"The user is visiting {destination} for {num_days} days and is "
        f"particularly interested in {interest}. "
        f"Here are the top attractions in the city:\n"
        f"{attractions_list}\n\n"
        f"Based on these locations and the user's interest in {interest}, "
        f"create a {num_days}-day travel itinerary. "
        f"Do your best to creatively weave the interest into the experience, "
        f"even if none of the attractions directly relate to it. "
        f"This can include recommending interest-themed restaurants, music, "
        f"events, local expressions, or mood-based experiences. "
        f"Each day's plan should be 4–5 sentences long, combining activities and meals. "
        f"Avoid long descriptions. Use a friendly and concise tone. "
        f"Include one local-language phrase or greeting each day.")

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=
        "You are a helpful travel planner. Your tone is concise, warm, and culturally aware.",
    )
    response = model.generate_content(prompt)

    return response.text
