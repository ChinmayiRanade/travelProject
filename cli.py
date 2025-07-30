from yelpApi import get_attractions  # re-exported by this module
from prompt import get_itinerary
from database import SessionLocal, create_db_and_tables, Travel, Landmark
from sqlalchemy import func
from sqlalchemy.orm import joinedload




def save_plan(destination, attractions, user_id=None):
   """
   Save the travel plan and attractions to database.
   If user_id is provided, the plan is scoped to that user.
   """
   with SessionLocal() as db:
       new_travel_plan = Travel(
           destination=destination,
           num_places=len(attractions),
           user_id=user_id
       )


       for place in attractions:
           new_landmark = Landmark(
               name=place["name"],
               address=place["address"],
               rating=place["rating"],
               url=place["url"],
               image_url=place.get("image_url", "")
           )
           new_travel_plan.landmarks.append(new_landmark)


       db.add(new_travel_plan)
       db.commit()
       db.refresh(new_travel_plan)


   print(f"\n✅ Your travel plan has been saved with ID: {new_travel_plan.id}")




def view_saved_plan(plan_id=None, user_id=None):
   """
   Retrieve and display a saved travel plan from database.
   Optionally scope by user_id.
   """
   if plan_id is None:
       try:
           plan_id = int(input("Enter the id of the plan you want to view: "))
       except ValueError:
           print("Invalid ID. Please enter a number.")
           return


   with SessionLocal() as db:
       q = (db.query(Travel)
              .options(joinedload(Travel.landmarks))
              .filter(Travel.id == plan_id))
       if user_id is not None:
           q = q.filter(Travel.user_id == user_id)


       plan = q.first()


       if not plan:
           print(f"No travel plan found with ID: {plan_id}")
           return


       print("\n--- Saved Travel Plan ---")
       print(f"Destination: {plan.destination}")
       print(f"Number of saved attractions: {plan.num_places}")
       print("\nAttractions")
       for i, landmark in enumerate(plan.landmarks, 1):
           print(f"  {i}. {landmark.name}")
           print(f"     📍 Address: {landmark.address}")
           print(f"     ⭐ Rating: {landmark.rating}")
           print(f"     🔗 More info: {landmark.url}\n")
       print("--- End of Plan ---")




def view_all_plans(user_id=None):
   """
   Retrieve and display a summary of saved travel plans.
   If user_id is provided, filter to only that user's plans.
   """
   with SessionLocal() as db:
       q = db.query(Travel)
       if user_id is not None:
           q = q.filter(Travel.user_id == user_id)


       all_plans = q.order_by(Travel.id.desc()).all()


       if not all_plans:
           print("\nNo travel plans have been saved yet.")
           return []


       print("\n--- Saved Travel Plans ---")
       for plan in all_plans:
           print(f"  ID: {plan.id:<3} | Destination: {plan.destination}")
       print("------------------------------")
       if user_id is None:
           print("(All users shown; pass user_id to scope to a single user.)")
       else:
           print("(Only this user's plans are shown.)")


       return all_plans




def check_db_for_destination(destination_name, user_id=None):
   """
   Check the database for a previously saved plan for a destination.
   If user_id is provided, limit to that user's plans.
   Returns a list of attraction dicts if found, else None.
   """
   with SessionLocal() as db:
       q = (db.query(Travel)
              .options(joinedload(Travel.landmarks))
              .filter(func.lower(Travel.destination) == destination_name.lower())
              .order_by(Travel.id.desc()))
       if user_id is not None:
           q = q.filter(Travel.user_id == user_id)


       plan = q.first()


       if plan:
           print(
               f"\n💡 Found a previously saved plan for {plan.destination}!"
               " Using saved attractions."
           )
           attractions = []
           for landmark in plan.landmarks:
               attractions.append(
                   {
                       "name": landmark.name,
                       "address": landmark.address,
                       "rating": landmark.rating,
                       "url": landmark.url,
                       "image_url": landmark.image_url or "",
                   }
               )
           return attractions
   return None




# ---------------------------
# CLI flow (unchanged)
# ---------------------------


def plan_new_trip():
   """Guide the user through planning a new trip (CLI only, not scoped)."""
   destination = input("Enter a city for your travel itinerary: ")
   days = input("How many days are you traveling for? ")
   interests = input(
       "What are some of your interests (history, food, coding, music)? "
   )
   budget = input("What is your approximate daily budget in USD? ")
   try:
       budget = int(budget)
   except ValueError:
       print("Please enter a valid number for your budget.")
       return


   try:
       num_days = int(days)
       if num_days <= 0:
           print("Number of days must be a positive number")
           return
   except ValueError:
       print("Please enter a valid number for days")
       return


   attractions = check_db_for_destination(destination)  # CLI: global


   if not attractions:
       print(
           f"\n🔎 No saved data found. "
           f"Finding attractions in {destination} via Yelp API..."
       )
       attractions = get_attractions(destination, num_days)


   if not attractions:
       print(
           f"Could not find any attractions for '{destination}'."
           "Please try another city."
       )
       return


   print("\n📍 Here are the attractions we'll use for your itinerary:\n")
   for i, place in enumerate(attractions, 1):
       print(f"{i}. {place['name']}")
       print(f"  ⭐ Rating: {place['rating']} | 📍 Address: {place['address']}")


   print("\n🤖 Generating your personalized itinerary with Gemini AI...")
   itinerary_text = get_itinerary(
       destination, num_days, interests, attractions, budget
   )


   if itinerary_text:
       print("\n✨ Your Custom Itinerary ✨")
       print(itinerary_text)
       save_plan(destination, attractions)  # CLI: global
   else:
       print("Sorry, could not generate an itinerary at this time.")




def show_menu():
   """Show menu."""
   print("\n✈️ Bon Voyage: Your Personal Travel Planner ✈️")
   print("---------------------------------------------")
   print("0. Show Menu Again")
   print("1. Plan a New Trip")
   print("2. View a specific Saved Trip")
   print("3. View all saved trips")
   print("4. Exit")
   print("---------------------------------------------")




def main():
   """Show main menu."""
   create_db_and_tables()
   show_menu()


   while True:
       choice = input("\nEnter your choice: ")


       if choice == "0":
           show_menu()


       elif choice == "1":
           plan_new_trip()
           show_menu()


       elif choice == "2":
           try:
               plan_id = int(input("Enter the id of the plan you want to view: "))
           except ValueError:
               print("Invalid ID. Please enter a number.")
               continue
           view_saved_plan(plan_id=plan_id)  # CLI: global
           show_menu()


       elif choice == "3":
           view_all_plans()  # CLI: global
           show_menu()


       elif choice == "4":
           print("Bon Voyage!")
           break


       else:
           print(
               """Invalid option, type 0 to see menu again.
           Choose 0, 1, 2, 3, 4"""
           )




if __name__ == "__main__":
   main()


