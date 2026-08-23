# tests/unit/test_event_service.py
#
# Pure unit tests for EventService with mocked DAOs.
# WHY: Event lifecycle encompasses creation, validation of foreign keys (category, venue, creator),
# status transitions ('draft' -> 'published'), and search/filtering.

import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
from Services.event_service import EventService
from models.event import Event
from models.category import Category
from models.venue import Venue
from models.user import User


@pytest.mark.unit
class TestEventService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.event_service = EventService()
        self.mock_event_dao = MagicMock()
        self.mock_cat_dao = MagicMock()
        self.mock_venue_dao = MagicMock()
        self.mock_user_dao = MagicMock()

        self.event_service.event_dao = self.mock_event_dao
        self.event_service.category_dao = self.mock_cat_dao
        self.event_service.venue_dao = self.mock_venue_dao
        self.event_service.user_dao = self.mock_user_dao

    def test_create_event_success(self):
        """WHY: Valid event creation verifies category/venue/user existence and persists event with 201."""
        self.mock_cat_dao.get_category_by_id.return_value = Category(id=1, name="Music")
        self.mock_venue_dao.get_venue_by_id.return_value = Venue(id=2, name="Hall")
        self.mock_user_dao.get_user_by_id.return_value = User(id=1, name="Admin")

        fake_ev = Event(
            id=10,
            title="Rock Festival",
            category_id=1,
            venue_id=2,
            created_by=1,
            event_date=date.today() + timedelta(days=5),
            start_time="19:00",
            base_price=50.00,
            status="draft",
        )
        self.mock_event_dao.create_event.return_value = fake_ev

        res = self.event_service.create_event({
            "title": "Rock Festival",
            "category_id": 1,
            "venue_id": 2,
            "created_by": 1,
            "event_date": str(date.today() + timedelta(days=5)),
            "start_time": "19:00",
            "base_price": 50.00,
        })
        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["title"] == "Rock Festival"

    def test_create_event_invalid_category_fails(self):
        """WHY: Creating event under non-existent category returns 404 Not Found."""
        self.mock_cat_dao.get_category_by_id.return_value = None
        res = self.event_service.create_event({
            "title": "Invalid Cat Event",
            "category_id": 999,
            "venue_id": 1,
            "created_by": 1,
            "event_date": str(date.today() + timedelta(days=5)),
            "start_time": "19:00",
        })
        assert res["success"] is False
        assert res["status"] == 404
        assert "Category" in res["message"]

    def test_create_event_invalid_venue_fails(self):
        """WHY: Creating event under non-existent venue returns 404 Not Found."""
        self.mock_cat_dao.get_category_by_id.return_value = Category(id=1, name="Art")
        self.mock_venue_dao.get_venue_by_id.return_value = None

        res = self.event_service.create_event({
            "title": "Invalid Venue Event",
            "category_id": 1,
            "venue_id": 999,
            "created_by": 1,
            "event_date": str(date.today() + timedelta(days=5)),
            "start_time": "19:00",
        })
        assert res["success"] is False
        assert res["status"] == 404
        assert "Venue" in res["message"]

    def test_publish_event_status_transition(self):
        """WHY: Publishing an event flips status from 'draft' to 'published'."""
        fake_ev = Event(id=5, title="Draft Event", status="draft")
        self.mock_event_dao.get_event_by_id.return_value = fake_ev

        res = self.event_service.update_event(5, {"status": "published"})
        assert res["success"] is True
        assert fake_ev.status == "published"
        self.mock_event_dao.update_event.assert_called_once_with(fake_ev)

    def test_search_events(self):
        """WHY: Event search delegates query parameters to DAO and returns results."""
        self.mock_event_dao.search_events.return_value = [Event(id=1, title="Jazz Night")]
        res = self.event_service.search_events("Jazz")
        assert res["success"] is True
        assert len(res["data"]) == 1
        assert res["data"][0]["title"] == "Jazz Night"
