import os
import google.generativeai as genai
from yelpApi import get_attractions


genai.configure(api_key=os.getenv("GENAI_KEY"))

# destination = input("Enter a city for your travel itinerary: ")
# days = input("How many days are you traveling for? ")
# interest = input("What are your interests: ")

def itinerary_generator(destination, num_days, interest):
   
    attractions = get_attractions(destination)
    names = []
    
    print("\n:round_pushpin: Top attractions from Yelp:\n")

    for i, place in enumerate(attractions, 1):
        print(f"{i}. {place['name']}")
        print(f"   :round_pushpin: Address: {place['address']}")
        print(f"   :star: Rating: {place['rating']}")
        print(f"   :link: More info: {place['url']}\n")
        line = f"- {place['name']} ({place['address']}, Rating: {place['rating']})"
        names.append(line)
        
    attractions_list = "\n".join(names)
    
    prompt = (
        f"You are a helpful and culturally aware travel planner. "
        f"The user is visiting {destination} for {days} days and is "
        f"particularly interested in {interest}. "
        f"Here are the top attractions in the city:\n"
        f"{attractions_list}\n\n"
        f"Based on these locations and the user's interest in {interest}, "
        f"create a {days}-day travel itinerary. "
        f"Do your best to creatively weave the interest into the experience, "
        f"even if none of the attractions directly relate to it. "
        f"This can include recommending interest-themed restaurants, music, "
        f"events, local expressions, or mood-based experiences. "
        f"Each day's plan should be 4–5 sentences long, combining activities and meals. "
        f"Avoid long descriptions. Use a friendly and concise tone. "
        f"Include one local-language phrase or greeting each day."
        f"You are a creative and personalized trip planner. The user is visiting "
        f"{destination} for {days} days and is passionate about {interest}. "
        f"Use the attractions below to craft a meaningful itinerary:\n"
        f"{attractions_list}\n\n"
        f"Suggest activities and meals that align with the interest. If "
        f"the interest is not clearly matched, draw creative connections. "
        f"Each day should be 4–5 sentences. End each day with a local phrase."
        f"As a travel planner, design a {days}-day itinerary in {destination}. "
        f"The traveler is interested in {interest}. Use these attractions:\n"
        f"{attractions_list}\n\n"
        f"For each day:\n"
        f"- Suggest 1–2 main activities.\n"
        f"- Recommend a meal spot.\n"
        f"- Weave in the interest area if possible.\n"
        f"- End with a greeting in the local language.\n"
        f"Keep each day short, warm, and informative."
    )
    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     config=types.GenerateContentConfig(
    #         system_instruction="You are a helpful travel planner. Your tone is concise, warm, and culturally aware.",
    #     ),
    #     contents=prompt,
    # )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are a helpful travel planner. Your tone is concise, warm, and culturally aware.",
    )
    response = model.generate_content(prompt)
    print("\nGenerated itinerary:")
    print(response.text)
    return response.json()

