import os
import unittest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Travel, Landmark


class TestDatabaseRelationships(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.test_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(
            self.test_url, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()  # release connection pool
        os.close(self.db_fd)  # close the OS file descriptor
        os.remove(self.db_path)

    def test_travel_landmark_relationship(self):
        travel = Travel(destination="Tokyo", num_places=2)
        travel.landmarks = [
            Landmark(name="Shibuya", address="Tokyo", rating=4.0, url="url1"),
            Landmark(name="Tower", address="Tokyo", rating=4.5, url="url2"),
        ]
        self.db.add(travel)
        self.db.commit()

        saved = self.db.query(Travel).filter_by(destination="Tokyo").first()
        self.assertEqual(len(saved.landmarks), 2)
