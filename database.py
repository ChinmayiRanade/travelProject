import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.engine.url import make_url


# Use DATABASE_URL if provided (e.g., Render/Postgres), else local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///travel_plans.db")
url = make_url(DATABASE_URL)


engine_kwargs = {}
# SQLite needs this connect arg; Postgres/MySQL don't
if url.get_backend_name().startswith("sqlite"):
   engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
   # Good production default to keep connections healthy
   engine_kwargs["pool_pre_ping"] = True


# Set echo=True temporarily if you want to debug SQL locally
engine = create_engine(DATABASE_URL, echo=True, **engine_kwargs)


# Important: prevent attribute expiration after commit (avoids DetachedInstanceError)
SessionLocal = sessionmaker(
   autocommit=False,
   autoflush=False,
   bind=engine,
   expire_on_commit=False
)


Base = declarative_base()


# ------------------------
# ORM Models
# ------------------------


class User(Base):
   __tablename__ = "users"


   id = Column(Integer, primary_key=True, index=True)
   username = Column(String, unique=True, nullable=False, index=True)
   email = Column(String, unique=True, nullable=False)
   hashed_password = Column(String, nullable=False)


   travels = relationship("Travel", back_populates="user", cascade="all, delete-orphan")




class Travel(Base):
   __tablename__ = "userinput_travel"


   id = Column(Integer, primary_key=True, index=True)
   destination = Column(String, index=True)
   num_places = Column(Integer)


   user_id = Column(Integer, ForeignKey("users.id"))
   user = relationship("User", back_populates="travels")


   landmarks = relationship(
       "Landmark", back_populates="travel", cascade="all, delete-orphan"
   )




class Landmark(Base):
   __tablename__ = "landmarks"


   id = Column(Integer, primary_key=True, index=True)
   name = Column(String)
   address = Column(String)
   rating = Column(Float)
   url = Column(String)
   image_url = Column(String)


   travel_id = Column(Integer, ForeignKey("userinput_travel.id"))
   travel = relationship("Travel", back_populates="landmarks")




def create_db_and_tables():
   Base.metadata.create_all(bind=engine)


