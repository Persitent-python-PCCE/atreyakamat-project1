# tests/integration/test_api_booking.py
#
# Integration test for complete booking workflow:
# Hold seat -> Confirm booking -> Review history -> Check ticket generation.
# WHY: Verifies multi-stage customer checkout process across seats, holds, bookings, rewards, and tickets.

import pytest


@pytest.mark.integration
class TestApiBookingIntegration:
    def test_full_seated_booking_api_flow(self, client, auth_headers_customer, event, seat):
        """WHY: End-to-end: Hold seat -> Confirm Booking -> Check History -> Verify Ticket token."""
        # 1. Hold seat
        res_hold = client.post(
            f"/api/events/{event.id}/seats/{seat.id}/hold",
            headers=auth_headers_customer,
        )
        assert res_hold.status_code == 201

        # 2. Confirm booking
        res_confirm = client.post("/api/checkout/confirm", headers=auth_headers_customer, json={
            "event_id": event.id,
        })
        assert res_confirm.status_code == 201
        b_data = res_confirm.get_json()["data"]
        assert b_data["total_amount"] == 75.00
        assert b_data["cashback_amount"] == 1.50
        assert "TKT-" in b_data["ticket_token"]

        # 3. Verify in user booking history
        res_hist = client.get("/api/bookings/my", headers=auth_headers_customer)
        assert res_hist.status_code == 200
        assert len(res_hist.get_json()["data"]) == 1
