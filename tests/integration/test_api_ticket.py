# tests/integration/test_api_ticket.py
#
# Integration test for Ticket generation, lookup, and QR scan verification.
# WHY: Verifies that issued tickets can be retrieved and validated by venue staff at the gate.

import pytest
from models.booking import Booking
from models.ticket import Ticket


@pytest.mark.integration
class TestApiTicketIntegration:
    def test_verify_and_anti_double_scan(self, client, db_session, event, customer_user, auth_headers_admin):
        """WHY: Validates first scan admission and enforces anti-double scan protection."""
        booking = Booking(user_id=customer_user.id, event_id=event.id, booking_reference="SMU-TKT-INT-999", status="confirmed")
        db_session.add(booking)
        db_session.commit()

        ticket = Ticket(booking_id=booking.id, ticket_token="TKT-INT-VALID-999", ticket_status="valid")
        db_session.add(ticket)
        db_session.commit()

        # 1. Valid scan
        res1 = client.post("/api/tickets/verify", headers=auth_headers_admin, json={
            "ticket_token": "TKT-INT-VALID-999",
            "mark_as_used": True,
        })
        assert res1.status_code == 200

        # 2. Second scan
        res2 = client.post("/api/tickets/verify", headers=auth_headers_admin, json={
            "ticket_token": "TKT-INT-VALID-999",
            "mark_as_used": True,
        })
        assert res2.status_code == 409
