# tests/unit/test_event_addon_service.py
#
# Pure unit tests for EventAddonService.
# Verifies CRUD operations on event add-ons with mocked DAOs.

import pytest
from unittest.mock import MagicMock
from Services.event_addon_service import EventAddonService
from models.event_addon import EventAddon
from models.event import Event


@pytest.mark.unit
class TestEventAddonService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.service = EventAddonService()
        self.mock_addon_dao = MagicMock()
        self.mock_event_dao = MagicMock()

        self.service.addon_dao = self.mock_addon_dao
        self.service.event_dao = self.mock_event_dao

    def test_create_addon_success(self):
        """Creates an addon when valid event and data provided."""
        self.mock_event_dao.get_event_by_id.return_value = Event(id=1, title="Festival")
        mock_saved = EventAddon(
            id=10,
            event_id=1,
            name="VIP Pass",
            description="Access to VIP lounge",
            price=250.00,
            available_quantity=50,
            is_active=True,
        )
        self.mock_addon_dao.create_addon.return_value = mock_saved

        payload = {
            "event_id": 1,
            "name": "VIP Pass",
            "description": "Access to VIP lounge",
            "price": 250.00,
            "available_quantity": 50,
            "is_active": True,
        }
        res = self.service.create_addon(payload)
        assert res["success"] is True
        assert res["data"]["name"] == "VIP Pass"
        assert res["data"]["price"] == 250.00

    def test_create_addon_missing_name_or_event(self):
        """Fails when name or event_id is missing."""
        res1 = self.service.create_addon({"event_id": 1, "name": ""})
        assert res1["success"] is False
        assert "Missing required field: name" in res1["message"]

        res2 = self.service.create_addon({"name": "VIP Pass"})
        assert res2["success"] is False
        assert "Missing required field: event_id" in res2["message"]

    def test_create_addon_event_not_found(self):
        """Fails when target event does not exist."""
        self.mock_event_dao.get_event_by_id.return_value = None
        res = self.service.create_addon({"event_id": 999, "name": "VIP Pass"})
        assert res["success"] is False
        assert "Event not found" in res["message"]

    def test_get_addon_by_id(self):
        """Retrieves single addon by ID."""
        addon = EventAddon(id=5, event_id=1, name="Popcorn", price=50.00, available_quantity=100, is_active=True)
        self.mock_addon_dao.get_addon_by_id.return_value = addon

        res = self.service.get_addon_by_id(5)
        assert res["success"] is True
        assert res["data"]["name"] == "Popcorn"

        self.mock_addon_dao.get_addon_by_id.return_value = None
        res_none = self.service.get_addon_by_id(999)
        assert res_none["success"] is False
        assert "Add-on not found" in res_none["message"]

    def test_update_addon(self):
        """Updates addon properties."""
        addon = EventAddon(id=5, event_id=1, name="Popcorn", price=50.00, available_quantity=100, is_active=True)
        self.mock_addon_dao.get_addon_by_id.return_value = addon
        self.mock_addon_dao.update_addon.return_value = addon

        res = self.service.update_addon(5, {"name": "Large Popcorn", "price": 80.00, "is_active": False})
        assert res["success"] is True
        assert res["data"]["name"] == "Large Popcorn"
        assert res["data"]["price"] == 80.00
        assert res["data"]["is_active"] is False

    def test_delete_addon(self):
        """Deletes addon by ID."""
        addon = EventAddon(id=5, event_id=1, name="Popcorn")
        self.mock_addon_dao.get_addon_by_id.return_value = addon
        self.mock_addon_dao.delete_addon.return_value = None

        res = self.service.delete_addon(5)
        assert res["success"] is True
        assert "deleted" in res["message"]
