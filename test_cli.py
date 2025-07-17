import unittest
import os
from unittest.mock import patch, MagicMock

# Set fake API keys for testing
os.environ["YELP_API_KEY"] = "fake-key-for-tests"
os.environ["GENAI_KEY"] = "fake-genai-key-for-tests"

# Create database tables before tests run
from database import engine, Base

def setup_module(module):
    Base.metadata.create_all(bind=engine)

# Mock google.generativeai globally before importing cli
with patch.dict('sys.modules', {
    'google': MagicMock(),
    'google.generativeai': MagicMock()
}):
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

    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.refresh = MagicMock()
    mock_session.close = MagicMock()

    save_plan("Testville", mock_attractions, db=mock_session)

    assert mock_session.add.call_count == 3
    assert mock_session.commit.call_count == 2
    assert mock_session.refresh.called



@patch("builtins.input", side_effect=["999"])
def test_view_saved_plan_with_invalid_id(mock_input):
    with patch('cli.SessionLocal') as MockSession:
        mock_session = MockSession.return_value.__enter__.return_value
        mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

        view_saved_plan()
