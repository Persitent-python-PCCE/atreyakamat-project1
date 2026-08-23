# tests/controllers/test_web_controllers.py
#
# Controller tests for Jinja2 web page rendering.
# WHY: Ensures server-rendered HTML pages render successfully without template syntax errors.

import pytest


@pytest.mark.controller
class TestWebControllers:
    def test_home_page_renders_successfully(self, client):
        """WHY: Public homepage renders 200 with branding."""
        res = client.get("/")
        assert res.status_code == 200
        assert b"SeatMeUp" in res.data

    def test_events_page_renders_successfully(self, client, event):
        """WHY: Events browsing web page lists active events."""
        res = client.get("/events")
        assert res.status_code == 200
        assert b"Beethoven" in res.data

    def test_event_detail_page_renders_successfully(self, client, event):
        """WHY: Single event page renders with description and seat map container."""
        res = client.get(f"/events/{event.id}")
        assert res.status_code == 200
        assert b"Beethoven" in res.data
