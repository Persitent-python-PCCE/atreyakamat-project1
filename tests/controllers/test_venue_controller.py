# tests/controllers/test_venue_controller.py
#
# Controller tests for Venue API endpoints (/api/venues/*).
# WHY: Verifies Venue CRUD API endpoints for administrative venue configuration.

import pytest


@pytest.mark.controller
class TestVenueController:
    def test_venue_crud_api_flow(self, client, auth_headers_admin):
        """WHY: Admin can create, read, update, and delete venues via REST endpoints."""
        # 1. Create Venue
        res_create = client.post("/api/venues", headers=auth_headers_admin, json={
            "name": "Metropolitan Opera",
            "address": "30 Lincoln Center Plaza",
            "city": "New York",
            "state": "NY",
            "capacity": 3800,
            "venue_type": "seated",
        })
        assert res_create.status_code == 201
        venue_id = res_create.get_json()["data"]["id"]

        # 2. Get Venue Details
        res_get = client.get(f"/api/venues/{venue_id}")
        assert res_get.status_code == 200
        assert res_get.get_json()["data"]["name"] == "Metropolitan Opera"

        # 3. Update Venue
        res_update = client.put(f"/api/venues/{venue_id}", headers=auth_headers_admin, json={
            "name": "The Met Opera",
            "capacity": 4000,
        })
        assert res_update.status_code == 200
        assert res_update.get_json()["data"]["name"] == "The Met Opera"

        # 4. Delete Venue
        res_del = client.delete(f"/api/venues/{venue_id}", headers=auth_headers_admin)
        assert res_del.status_code == 200
