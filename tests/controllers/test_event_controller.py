# tests/controllers/test_event_controller.py
#
# Controller tests for Event API endpoints (/api/events/*).
# WHY: Verifies public explore/search and protected admin event creation routes.

import pytest
from datetime import date, timedelta


@pytest.mark.controller
class TestEventController:
    def test_list_and_search_events_api(self, client, event):
        """WHY: Public exploration and search routes return serialized events matching query filters."""
        # 1. Explore events
        res = client.get("/api/events")
        assert res.status_code == 200
        assert len(res.get_json()["data"]) >= 1

        # 2. Event details
        res_detail = client.get(f"/api/events/{event.id}")
        assert res_detail.status_code == 200
        assert res_detail.get_json()["data"]["title"] == event.title

        # 3. Search events
        res_search = client.get("/api/events/search?q=Beethoven")
        assert res_search.status_code == 200
        assert len(res_search.get_json()["data"]) >= 1

    def test_admin_create_event_api(self, client, auth_headers_admin, category, venue):
        """WHY: Authenticated admin can create new events via POST /api/events."""
        res = client.post("/api/events", headers=auth_headers_admin, json={
            "title": "Chamber Orchestra",
            "category_id": category.id,
            "venue_id": venue.id,
            "event_date": str(date.today() + timedelta(days=20)),
            "start_time": "18:00",
            "base_price": 55.00,
        })
        assert res.status_code == 201
        assert res.get_json()["data"]["title"] == "Chamber Orchestra"
