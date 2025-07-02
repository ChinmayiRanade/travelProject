# README file

## Bon Voyage: Your Personal AI Travel Planner
Bon Voyage is an intelligent command-line application that crafts personalized travel itineraries. It combines real-time, high-quality attraction data from the Yelp API with the creative power of Google's Gemini AI to build unique travel plans tailored to your specific interests. All plans are saved locally in a database, and the app is smart enough to use cached data to avoid redundant API calls, saving you time and resources.

## Core Features
- **Personalized Itineraries**: Moves beyond generic "Top 10" lists by generating plans based on your unique interests (e.g., "history," "jazz music," "local food").
- **Real-World Data**: Pulls up-to-date, top-rated landmarks, parks, and museums directly from the Yelp API.
- **Intelligent Caching**: Checks its local database for a destination before calling the Yelp API. If you've planned a trip to a city before, it re-uses the attraction data, making the app faster and more efficient.
- **Local Database Storage**: Saves all your travel plans and their associated attractions using SQLAlchemy and a local SQLite database.
- **View Past Trips**: Easily retrieve and view the details of any previously generated travel plan using its unique ID.
- **Simple & Interactive CLI**: An easy-to-use command-line interface makes planning your next trip a breeze.

## How It Works (Architecture and flow)
1. **User Input**: The user provides a destination, number of days, and personal interests via the command-line interface (cli.py).
2. **Database Check**: The app first queries its local SQLite database (travel_plans.db) to see if attraction data for that destination has already been saved.
3. **API Call (If Needed)**: If no data is found, the app calls the Yelp Fusion API to fetch a list of top-rated attractions (yelpApi.py).
4. **AI Itinerary Generation**: The curated list of attractions (from the database or Yelp) and the user's interests are formatted into a detailed prompt, which is sent to the Google Gemini AI (prompt.py).
5. **Display and Save**: The AI-generated itinerary is displayed to the user. The new travel plan, along with its list of attractions, is then saved to the SQLite database for future use (database.py and cli.py).

## ⚙️ Setup and Installation

**Follow these steps to get the Bon Voyage application running on your local machine.**

#### Prerequisites
- Python 3.7+
- A Yelp Fusion API Key
- A Google Gemini (Generative AI) API Key

#### Step 1: Clone the Repository
```
git clone git@github.com:ChinmayiRanade/travelProject.git
cd travelProject
```
#### Step 2: Create a Virtual Environment
**On macOS / Linux**
```
python3 -m venv venv
source venv/bin/activate
```
**On Windows**
```
python -m venv venv
.\venv\Scripts\activate
```

#### Step 3: Install Dependencies
The required Python packages are listed in `requirements.txt`. Install them with pip:

`pip install -r requirements.txt`

(If a requirements.txt file is not present, you can install the packages manually: `pip install requests python-dotenv google-generativeai SQLAlchemy`)

#### Step 4: Set Up Your API Keys
The application uses a `.env` file to securely manage your API keys.
Create a new file named `.env` in the root directory of the project.
Copy the following format into your `.env` file and replace the placeholder text with your actual API keys.
```
# .env

# Get your Yelp API key from the Yelp Fusion Developer Portal
# https://www.yelp.com/developers/documentation/v3/authentication
YELP_API_KEY="YOUR_YELP_API_KEY_HERE"

# Get your Gemini API key from Google AI Studio
# https://ai.google.dev/
GENAI_KEY="YOUR_GOOGLE_GEMINI_API_KEY_HERE"

```

**You are now ready to run the application!**

🚀 How to Operate the App
1. **Run the Application**
Navigate to the project's root directory in your terminal and run the main script:
`python cli.py`

2. **Main Menu**
You will be greeted with the main menu:

```
✈️ Bon Voyage: Your Personal Travel Planner ✈️
1. Plan a new trip
2. View a saved trip
3. Exit

Enter your choice:
```

3. **Plan a New Trip**
Enter 1 and press Enter.
The app will prompt you for a city, the number of days, and your interests.
Example Session:
```
Enter your choice: 1
Enter a city for your travel itinerary: Paris
How many days are you traveling for? 3
What are some of your interests (e.g., history, food, music)? impressionist art and bakeries

🔎 No saved data found. Finding top attractions in Paris via Yelp API...

📍 Here are the attractions we'll use for your itinerary:

1. Musée d'Orsay
   ⭐ Rating: 5.0 | 📍 Address: 1 rue de la Légion d'Honneur, 75007 Paris, France
2. Louvre Museum
   ⭐ Rating: 4.5 | 📍 Address: Rue de Rivoli, 75001 Paris, France
...

🤖 Generating your personalized itinerary with Gemini AI...

✨ Your Custom Itinerary ✨
Here is a delightful 3-day itinerary for your trip to Paris, blending world-class art with the simple joy of a perfect croissant!

**Day 1:** Start your Parisian adventure with a visit to the Musée d'Orsay, a haven for Impressionist art located in a stunning former train station. After immersing yourself in Monet and Degas, take a short walk to find a classic boulangerie like Poilâne for a delicious lunch. For a truly local greeting, say "**Bonjour!**" (Hello!) when you enter a shop.

... (full itinerary continues) ...

✅ Your travel plan for Paris has been saved with ID: 1
```

4. View a Saved Trip
From the main menu, enter 2 and press Enter.
The app will ask for the ID of the plan you wish to view. This ID is provided when you first create a plan.
Example Session:

```
Enter your choice: 2
Enter the ID of the travel plan you want to view: 1

--- Saved Travel Plan ---
Destination: Paris
Number of saved attractions: 9

Attractions:
  1. Musée d'Orsay
     📍 Address: 1 rue de la Légion d'Honneur, 75007 Paris, France
     ⭐ Rating: 5.0
     🔗 More info: https://www.yelp.com/biz/mus%C3%A9e-d-orsay-paris

... (list of all saved attractions continues) ...
--- End of Plan ---
```
5. **Exit the Application**
From the main menu, enter 3 to close the program.
