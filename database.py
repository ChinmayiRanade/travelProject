from sqlalchemy import create_engine, Column
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Use a file-based SQLite database
DATABASE_URL = "sqlite:///travel_plans.db"

# Boilerplate for SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship to Travel plans
    travels = relationship("Travel", back_populates="user", cascade="all, delete-orphan")

# Define the first table: Travel
class Travel(Base):
    __tablename__ = "userinput_travel"

    id = Column(Integer, primary_key=True, index=True)
    destination = Column(String, index=True)
    num_places = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="travels")

    # This creates a link to the Landmark table
    landmarks = relationship(
        "Landmark", back_populates="travel", cascade="all, delete-orphan"
    )


class Landmark(Base):
    # Define the second table: Landmark
    __tablename__ = "landmarks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    rating = Column(Float)
    url = Column(String)

    # Foreign key to link back to the Travel table
    travel_id = Column(Integer, ForeignKey("userinput_travel.id"))
    travel = relationship("Travel", back_populates="landmarks")


def create_db_and_tables():
    # Function to create the database and tables if they don't exist
    Base.metadata.create_all(bind=engine)