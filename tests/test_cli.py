import unittest
from unittest.mock import patch, MagicMock
from cli import check_db_for_destination, save_plan, view_saved_plan


def test_check_db_for_destination_none_when_not_found():
    with patch('cli.SessionLocal') as MockSession:
        mock_session = MockSession.return_value.__enter__.return_value
        mock_session.query.return_value.options.return_value.filter.return_value.order_by.return_value.first.return_value = None

        result = check_db_for_destination("nowhere")
        assert result is None

def test_save_plan_creates_travel_and_landmarks():
    mock_attractions = [
        {"name": "Place A", "address": "123 St", "rating": 4.5, "url": "http://a.com"},
        {"name": "Place B", "address": "456 St", "rating": 4.8, "url": "http://b.com"},
    ]

    with patch('cli.SessionLocal') as MockSession:
        mock_session = MockSession.return_value.__enter__.return_value
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        save_plan("Testville", mock_attractions)

        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called

@patch("builtins.input", side_effect=["999"])
def test_view_saved_plan_with_invalid_id(mock_input):
    with patch('cli.SessionLocal') as MockSession:
        mock_session = MockSession.return_value.__enter__.return_value
        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

        view_saved_plan()