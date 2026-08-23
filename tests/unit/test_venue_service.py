# tests/unit/test_venue_service.py
#
# Pure unit tests for VenueService with mocked VenueDAO.
# WHY: Venues must uphold capacity constraints, valid venue types ('seated'/'general'),
# and prevent deletion if active events are currently bound to the venue.

import pytest
from unittest.mock import MagicMock
from Services.venue_service import VenueService
from models.venue import Venue
from models.event import Event


@pytest.mark.unit
class TestVenueService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.venue_service = VenueService()
        self.mock_dao = MagicMock()
        self.venue_service.venue_dao = self.mock_dao

    def test_get_venue_by_id_missing(self):
        """WHY: Non-existent venue ID returns 404."""
        self.mock_dao.get_venue_by_id.return_value = None
        res = self.venue_service.get_venue_by_id(999)
        assert res["success"] is False
        assert res["status"] == 404

    @pytest.mark.parametrize("payload, expected_msg", [
        ({"address": "123 Main"}, "name"),
        ({"name": "Hall"}, "address"),
    ])
    def test_create_venue_missing_required_fields(self, payload, expected_msg):
        """WHY: Name and address are mandatory venue attributes."""
        res = self.venue_service.create_venue(payload)
        assert res["success"] is False
        assert res["status"] == 400
        assert expected_msg in res["message"]

    def test_create_venue_negative_capacity(self):
        """WHY: Venue capacity must be non-negative."""
        res = self.venue_service.create_venue({
            "name": "Arena", "address": "100 St", "capacity": -50
        })
        assert res["success"] is False
        assert res["status"] == 400
        assert "capacity" in res["message"].lower()

    def test_create_venue_success(self):
        """WHY: Creating a venue with valid attributes creates record and returns 201."""
        fake_v = Venue(id=1, name="Madison Square", address="4 Penn Plaza", city="NY", state="NY", capacity=20000, venue_type="seated")
        self.mock_dao.create_venue.return_value = fake_v

        res = self.venue_service.create_venue({
            "name": "Madison Square",
            "address": "4 Penn Plaza",
            "city": "NY",
            "state": "NY",
            "capacity": 20000,
            "venue_type": "seated",
        })
        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["venue_type"] == "seated"

    def test_update_venue_fields(self):
        """WHY: Updating venue preserves existing properties while modifying updated attributes."""
        fake_v = Venue(id=1, name="Old", address="Old Addr", capacity=100)
        self.mock_dao.get_venue_by_id.return_value = fake_v

        res = self.venue_service.update_venue(1, {"name": "New", "capacity": 250})
        assert res["success"] is True
        assert fake_v.name == "New"
        assert fake_v.capacity == 250

    def test_delete_venue_with_associated_events_fails(self):
        """WHY: Business guard prevents deleting a venue with linked events to prevent orphan foreign keys."""
        fake_v = Venue(id=10, name="Busy Hall")
        fake_v.events = [Event(id=10, title="Existing Event")]
        self.mock_dao.get_venue_by_id.return_value = fake_v

        res = self.venue_service.delete_venue(10)
        assert res["success"] is False
        assert res["status"] == 400
        assert "associated events" in res["message"]

    def test_delete_venue_without_events_succeeds(self):
        """WHY: Empty venues without scheduled events can be safely deleted."""
        fake_v = Venue(id=10, name="Empty Hall")
        fake_v.events = []
        self.mock_dao.get_venue_by_id.return_value = fake_v

        res = self.venue_service.delete_venue(10)
        assert res["success"] is True
        self.mock_dao.delete_venue.assert_called_once_with(fake_v)
