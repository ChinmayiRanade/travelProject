import os



def get_itinerary(destination, num_days, interest, attractions, budget):
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
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GENAI_KEY"))

    names = []
    for p in attractions:
        line = f"- {p['name']} ({p['address']}, Rating: {p['rating']})"
        names.append(line)

    attractions_list = "\n".join(names)

    prompt = (
        f"You are a helpful and culturally aware travel planner. "
        f"The user is visiting {destination} for {num_days} days and is "
        f"""particularly interested in {interest}.
        They have a daily travel budget of ${budget}.\n\n"""
        f"Here are the top attractions in the city:\n"
        f"{attractions_list}\n\n"
        f"""Based on these locations, their interests,
        and the ${budget} daily budget,"""
        f"create a detailed {num_days}-day travel itinerary. "
        f"Each day must include:\n"
        f"""- Morning, afternoon, and evening activity
        (with time suggestions).\n"""
        f"- Mention which attraction is visited and when.\n"
        f"- Recommend a local meal (e.g., lunch/dinner) with cuisine type.\n"
        f"- Suggest an evening experience.\n"
        f"- Use one local-language greeting or phrase each day.\n"
        f"""- 💰 For each day, estimate how much the user might spend on:
        attraction tickets
        , food, transport, and extras. """
        f"Make sure the total stays within ${budget}.\n\n"
        f"""Use friendly tone, clear structure,
        and format the output with 'Day 1', 'Day 2', etc."""
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="""You are a helpful travel planner.
        Your tone is concise, warm, """
        "and culturally aware.",
    )

    try:
        response = model.generate_content(prompt)
        return response.text or "Itinerary could not be generated."
    except Exception as e:
        print(f"AI generation failed:", {e})
        return None
