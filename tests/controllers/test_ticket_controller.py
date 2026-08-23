# tests/controllers/test_ticket_controller.py
#
# Controller tests for Ticket API endpoints (/api/tickets/*).
# WHY: Verifies QR scan validation endpoint and anti-double scan 409 rejection via HTTP API.

import pytest
from models.booking import Booking
from models.ticket import Ticket


@pytest.mark.controller
class TestTicketController:
    def test_verify_ticket_api_flow(self, client, db_session, event, customer_user, auth_headers_admin):
        """WHY: Door scanning endpoint validates legitimate ticket on first scan (200) and rejects second scan (409)."""
        booking = Booking(user_id=customer_user.id, event_id=event.id, booking_reference="SMU-TKT-API-1", status="confirmed")
        db_session.add(booking)
        db_session.commit()

        ticket = Ticket(booking_id=booking.id, ticket_token="TKT-APIVALID123", ticket_status="valid")
        db_session.add(ticket)
        db_session.commit()

        # 1. First Scan -> Success (200)
        res1 = client.post("/api/tickets/verify", headers=auth_headers_admin, json={
            "ticket_token": "TKT-APIVALID123",
            "mark_as_used": True,
        })
        assert res1.status_code == 200
        assert res1.get_json()["success"] is True

        # 2. Second Scan -> 409 Already Used
        res2 = client.post("/api/tickets/verify", headers=auth_headers_admin, json={
            "ticket_token": "TKT-APIVALID123",
            "mark_as_used": True,
        })
        assert res2.status_code == 409
