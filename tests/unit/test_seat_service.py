# tests/unit/test_seat_service.py
#
# Pure unit tests for SeatService covering the critical 1-minute seat hold concurrency mechanism.
# WHY: The 1-minute seat hold is the core real-time concurrency barrier in SeatMeUp:
#   1. Placing a hold locks the seat from other buyers for 60 seconds.
#   2. Concurrent attempts from another buyer are rejected with 409 Conflict.
#   3. Already-booked seats are permanently blocked.
#   4. Expired holds automatically transition to 'expired' and allow reacquisition.

import pytest
from datetime import datetime, timedelta
from Services.seat_service import SeatService
from models.seat_hold import SeatHold
from models.booking import Booking
from models.booking_item import BookingItem


@pytest.mark.unit
class TestSeatService:
    @pytest.fixture(autouse=True)
    def setup_service(self, db_session, event, seat):
        self.seat_service = SeatService()
        self.db = db_session
        self.event = event
        self.seat = seat

    def test_hold_available_seat_success(self):
        """WHY: Placing a 1-minute hold creates active hold token and sets 60-second expiration."""
        res = self.seat_service.hold_seat(event_id=self.event.id, seat_id=self.seat.id, user_id=1)
        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["seat_id"] == self.seat.id
        assert "hold_token" in res["data"]

        # Check DB
        hold = self.db.query(SeatHold).filter_by(event_id=self.event.id, seat_id=self.seat.id).first()
        assert hold is not None
        assert hold.status == "active"

    def test_hold_already_booked_seat_rejected(self):
        """WHY: Booked seats are permanently sold and cannot be held by any user (409 Conflict)."""
        booking = Booking(user_id=1, event_id=self.event.id, booking_reference="SMU-SOLD1", status="confirmed")
        self.db.add(booking)
        self.db.commit()

        b_item = BookingItem(booking_id=booking.id, seat_id=self.seat.id, quantity=1, unit_price=50.0, total_price=50.0)
        self.db.add(b_item)
        self.db.commit()

        res = self.seat_service.hold_seat(event_id=self.event.id, seat_id=self.seat.id, user_id=2)
        assert res["success"] is False
        assert res["status"] == 409
        assert "already booked" in res["message"].lower()

    def test_hold_active_seat_held_by_other_user_rejected(self):
        """WHY: Concurrent hold attempt from User 2 while User 1 holds the seat is blocked with 409 Conflict."""
        hold1 = SeatHold(
            event_id=self.event.id,
            seat_id=self.seat.id,
            user_id=1,
            hold_token="HLD-USER1",
            status="active",
            held_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=50),
        )
        self.db.add(hold1)
        self.db.commit()

        # User 2 attempts to hold
        res = self.seat_service.hold_seat(event_id=self.event.id, seat_id=self.seat.id, user_id=2)
        assert res["success"] is False
        assert res["status"] == 409
        assert "held by another user" in res["message"].lower()

    def test_expired_hold_marked_expired_and_reacquired(self):
        """WHY: When 60s timer expires, status flips to 'expired' and a new user can acquire the seat."""
        hold1 = SeatHold(
            event_id=self.event.id,
            seat_id=self.seat.id,
            user_id=1,
            hold_token="HLD-EXPIRED",
            status="active",
            held_at=datetime.utcnow() - timedelta(minutes=5),
            expires_at=datetime.utcnow() - timedelta(minutes=4),  # Expired
        )
        self.db.add(hold1)
        self.db.commit()

        # User 2 attempts to acquire
        res = self.seat_service.hold_seat(event_id=self.event.id, seat_id=self.seat.id, user_id=2)
        assert res["success"] is True
        assert res["status"] == 201

        # Check that old hold flipped to expired
        self.db.expire_all()
        old_h = self.db.get(SeatHold, hold1.id)
        assert old_h.status == "expired"

    def test_release_seat_hold_success(self):
        """WHY: User manually deselecting seat immediately releases hold status to 'released'."""
        hold = SeatHold(
            event_id=self.event.id,
            seat_id=self.seat.id,
            user_id=5,
            hold_token="HLD-REL",
            status="active",
            held_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=1),
        )
        self.db.add(hold)
        self.db.commit()

        res = self.seat_service.release_seat_hold(event_id=self.event.id, seat_id=self.seat.id, user_id=5)
        assert res["success"] is True

        self.db.expire_all()
        h_after = self.db.get(SeatHold, hold.id)
        assert h_after.status == "released"
