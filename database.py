from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Use a file-based SQLite database
DATABASE_URL = "sqlite:///travel_plans.db"

# Boilerplate for SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Itinerary(Base):
    # Define the first table: Userinput_itinerary
    __tablename__ = "userinput_itinerary"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True)
    num_places = Column(Integer)
    generated_itinerary = Column(Text)  # Storing the JSON from Gemini

    # This creates a link to the Landmark table
    landmarks = relationship("Landmark", back_populates="itinerary")


class Landmark(Base):
    # Define the second table: Landmark
    __tablename__ = "landmarks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    rating = Column(Float)
    url = Column(String)

    # Foreign key to link back to the Itinerary table
    itinerary_id = Column(Integer, ForeignKey("userinput_itinerary.id"))
    itinerary = relationship("Itinerary", back_populates="landmarks")


def create_db_and_tables():
    # Function to create the database and tables if they don't exist
    Base.metadata.create_all(bind=engine)
