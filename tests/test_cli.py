import unittest
from unittest.mock import patch, MagicMock
from cli import save_plan, check_db_for_destination, view_saved_plan, plan_new_trip


class TestLCliFunctions(unittest.TestCase):
    @patch("cli.SessionLocal")
    def test_save_plan(self, mock_session):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db
        mock_add = db.add
        mock_commit = db.commit
        mock_refresh = db.refresh

        attractions = [
            {
                "name": "Place A",
                "address": "Address A",
                "rating": 4.5,
                "url": "http://a.com",
            },
            {
                "name": "Place B",
                "address": "Address B",
                "rating": 4.7,
                "url": "http://b.com",
            },
        ]

        save_plan("Paris", attractions)

        assert mock_add.called
        assert mock_commit.called
        assert mock_refresh.called

    @patch("cli.SessionLocal")
    def test_check_db_for_destination_found(self, mock_session):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db

        mock_landmark = MagicMock()
        mock_landmark.name = "Landmark"
        mock_landmark.address = "123 St"
        mock_landmark.rating = 4.5
        mock_landmark.url = "http://url.com"

        mock_plan = MagicMock()
        mock_plan.landmarks = [mock_landmark]
        db.query().options().filter().order_by().first.return_value = mock_plan

        result = check_db_for_destination("Paris")
        assert result is not None
        assert result[0]["name"] == "Landmark"

    @patch("builtins.input", side_effect=["1"])
    @patch("cli.SessionLocal")
    def test_view_saved_plan_found(self, mock_session, mock_input):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db

        mock_landmark = MagicMock()
        mock_landmark.name = "Landmark"
        mock_landmark.address = "123 St"
        mock_landmark.rating = 4.5
        mock_landmark.url = "http://url.com"

        mock_plan = MagicMock()
        mock_plan.destination = "Paris"
        mock_plan.num_places = 1
        mock_plan.landmarks = [mock_landmark]
        db.query().options().filter().first.return_value = mock_plan

        view_saved_plan()  # will print to stdout

    @patch("cli.SessionLocal")
    def test_save_plan_with_empty_attractions(self, mock_session):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db

        save_plan("EmptyCity", [])

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @patch("cli.SessionLocal")
    def test_check_db_for_destination_not_found(self, mock_session):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db
        db.query().options().filter().order_by().first.return_value = None

        result = check_db_for_destination("NowhereLand")
        self.assertIsNone(result)

    @patch("cli.SessionLocal")
    def test_check_db_for_destination_case_insensitive(self, mock_session):
        db = MagicMock()
        mock_session.return_value.__enter__.return_value = db

        mock_landmark = MagicMock()
        mock_landmark.name = "Museum"
        mock_landmark.address = "Street 1"
        mock_landmark.rating = 4.0
        mock_landmark.url = "http://museum.com"

        mock_plan = MagicMock()
        mock_plan.landmarks = [mock_landmark]
        db.query().options().filter().order_by().first.return_value = mock_plan

        result = check_db_for_destination("NeW yOrK")
        self.assertEqual(result[0]["name"], "Museum")

    @patch("builtins.input", side_effect=["invalid"])
    def test_view_saved_plan_invalid_input(self, mock_input):
        result = view_saved_plan()  # should not raise
        self.assertIsNone(result)

    @patch("builtins.input", side_effect=["Paris", "two", "food"])
    def test_plan_new_trip_invalid_days(self, mock_input):
        with patch("cli.check_db_for_destination"), patch("cli.get_attractions"), patch(
            "cli.get_itinerary"
        ), patch("cli.save_plan"):
            plan_new_trip()  # Should handle and print error without crash

    @patch("builtins.input", side_effect=["Paris", "2", "food"])
    @patch("cli.get_itinerary", return_value=None)
    @patch(
        "cli.get_attractions",
        return_value=[
            {
                "name": "Eiffel Tower",
                "address": "Champ de Mars",
                "rating": 4.7,
                "url": "http://eiffel.com",
            }
        ],
    )
    @patch("cli.check_db_for_destination", return_value=None)
    def test_plan_new_trip_no_itinerary(
        self, mock_check, mock_yelp, mock_prompt, mock_input
    ):
        plan_new_trip()  # Should handle None from get_itinerary and not crash


if __name__ == "__main__":
    unittest.main()
