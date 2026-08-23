# tests/controllers/test_booking_controller.py
#
# Controller tests for Booking API endpoints (/api/checkout/*, /api/bookings/*).
# WHY: Verifies confirmation, history lookup, and cancellation API routes.

import pytest
from datetime import date, timedelta, time
from models.event import Event


@pytest.mark.controller
class TestBookingController:
    def test_create_and_cancel_booking_api(self, client, db_session, customer_user, auth_headers_customer, category, venue):
        """WHY: End-to-end booking confirmation, customer history review, and cancellation flow."""
        # Create GA Event
        event = Event(
            title="GA Show",
            category_id=category.id,
            venue_id=venue.id,
            created_by=customer_user.id,
            event_date=date.today()+timedelta(days=3),
            start_time=time(19, 0, 0),
            base_price=30.0,
            requires_seats=False,
            booking_open=True,
            status="published",
        )
        db_session.add(event)
        db_session.commit()

        # 1. Confirm GA Booking
        res_book = client.post("/api/checkout/confirm", headers=auth_headers_customer, json={
            "event_id": event.id,
            "quantity": 2,
        })
        assert res_book.status_code == 201
        b_data = res_book.get_json()["data"]
        booking_id = b_data["booking_id"]
        assert b_data["total_amount"] == 60.00

        # 2. View Booking History
        res_history = client.get("/api/bookings/my", headers=auth_headers_customer)
        assert res_history.status_code == 200
        assert len(res_history.get_json()["data"]) == 1

        # 3. Cancel Booking
        res_cancel = client.post(f"/api/bookings/{booking_id}/cancel", headers=auth_headers_customer)
        assert res_cancel.status_code == 200
