from sqlalchemy import create_engine, Column
from sqlalchemy import Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Use a file-based SQLite database
DATABASE_URL = "sqlite:///travel_plans.db"

# Boilerplate for SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define the first table: Travel
class Travel(Base):
    __tablename__ = "userinput_travel"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True)
    num_places = Column(Integer)

    # This creates a link to the Landmark table
    landmarks = relationship(
        "Landmark", 
        back_populates="travel", 
        cascade="all, delete-orphan")


# Define the second table: Landmark
class Landmark(Base):
    __tablename__ = "landmarks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    rating = Column(Float)
    url = Column(String)

    # Foreign key to link back to the Travel table
    travel_id = Column(Integer, ForeignKey("userinput_travel.id"))
    travel = relationship("Travel", back_populates="landmarks")

# Function to create the database and tables if they don't exist
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
