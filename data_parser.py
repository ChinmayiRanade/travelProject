import json
from prompt import itinerary_generator
from yelpApi import get_attractions

from database import SessionLocal, create_db_and_tables, Itinerary, Landmark


create_db_and_tables()
db = SessionLocal()

yelp_data = get_attractions(destination, l)
# Save everything

new_travel = Itinerary(
    destination=destination,
    num_places=len(yelp_data)
)