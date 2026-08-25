# tests/unit/test_booking_idempotency.py
#
# Dedicated test suite for Idempotent Booking Confirmation.
# WHY: Guarantees that duplicate requests with the same Idempotency-Key
# safely return the existing booking without double charging, double seat consumption,
# duplicate tickets, duplicate cashback, or duplicate promo code increments.

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.promo_code import PromoCode
from models.booking import Booking
from models.ticket import Ticket
from models.reward_transaction import RewardTransaction
from models.promo_code_usage import PromoCodeUsage
from Services.booking_service import BookingService
from Services.seat_service import SeatService


@pytest.mark.unit
class TestBookingIdempotency:
    @pytest.fixture
    def test_setup(self, db_session):
        user1 = User(name="Alice Idemp", email="alice.idemp@example.com", password_hash="pw", role="customer", reward_balance=0.00)
        user2 = User(name="Bob Idemp", email="bob.idemp@example.com", password_hash="pw", role="customer", reward_balance=0.00)
        admin = User(name="Admin Idemp", email="admin.idemp@seatmeup.com", password_hash="pw", role="admin")
        cat = Category(name="Idemp Concerts")
        ven = Venue(name="Idemp Hall", address="101 Idemp Way", venue_type="seated", capacity=10)
        db_session.add_all([user1, user2, admin, cat, ven])
        db_session.commit()

        seat1 = Seat(venue_id=ven.id, seat_number="A1", section_name="Orchestra", price=100.00, is_active=True)
        seat2 = Seat(venue_id=ven.id, seat_number="A2", section_name="Orchestra", price=100.00, is_active=True)
        seat3 = Seat(venue_id=ven.id, seat_number="A3", section_name="Orchestra", price=100.00, is_active=True)
        db_session.add_all([seat1, seat2, seat3])

        promo = PromoCode(
            code="IDEMP10",
            discount_type="percentage",
            discount_value=10.00,
            minimum_booking_amount=0.00,
            max_uses=10,
            used_count=0,
            is_active=True,
        )
        db_session.add(promo)

        ev = Event(
            title="Idemp Live Symphony",
            category_id=cat.id,
            venue_id=ven.id,
            created_by=admin.id,
            event_date=date.today() + timedelta(days=20),
            start_time=time(19, 0),
            base_price=100.00,
            status="published",
            booking_open=True,
            requires_seats=True,
        )
        db_session.add(ev)
        db_session.commit()

        return {
            "user1": user1,
            "user2": user2,
            "admin": admin,
            "venue": ven,
            "seat1": seat1,
            "seat2": seat2,
            "seat3": seat3,
            "promo": promo,
            "event": ev,
        }

    # 1. First request succeeds
    def test_first_booking_request_succeeds(self, test_setup):
        seat_svc = SeatService()
        booking_svc = BookingService()

        # Hold seat
        hold_res = seat_svc.hold_seat(test_setup["event"].id, test_setup["seat1"].id, test_setup["user1"].id)
        assert hold_res["success"] is True

        res = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            promo_code="IDEMP10",
            idempotency_key="key-test-001",
        )
        assert res["success"] is True
        assert res["status"] == 201
        assert "booking_reference" in res["data"]
        assert res["data"]["total_amount"] == 90.00  # 100 - 10%

    # 2. Same request with same key returns same booking without duplicate creation
    def test_duplicate_key_returns_same_booking(self, test_setup, db_session):
        seat_svc = SeatService()
        booking_svc = BookingService()

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat1"].id, test_setup["user1"].id)

        res1 = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            promo_code="IDEMP10",
            idempotency_key="key-test-002",
        )
        assert res1["success"] is True
        b_ref1 = res1["data"]["booking_reference"]
        b_id1 = res1["data"]["booking_id"]

        # Retry with same idempotency key (even without active hold)
        res2 = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            promo_code="IDEMP10",
            idempotency_key="key-test-002",
        )
        assert res2["success"] is True
        assert res2["status"] == 200
        assert res2["data"]["booking_reference"] == b_ref1
        assert res2["data"]["booking_id"] == b_id1

        # Assert exactly one Booking in database
        all_bookings = Booking.query.filter_by(idempotency_key="key-test-002").all()
        assert len(all_bookings) == 1

    # 3. Same key from another user is rejected safely
    def test_same_key_different_user_rejected(self, test_setup):
        seat_svc = SeatService()
        booking_svc = BookingService()

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat1"].id, test_setup["user1"].id)
        booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            idempotency_key="key-shared-003",
        )

        # User 2 attempts to use same key
        res_user2 = booking_svc.confirm_booking(
            user_id=test_setup["user2"].id,
            event_id=test_setup["event"].id,
            idempotency_key="key-shared-003",
        )
        assert res_user2["success"] is False
        assert res_user2["status"] == 403

    # 4. Same booking cannot consume seat twice & cashback credited only once
    def test_cashback_and_promo_credited_only_once(self, test_setup, db_session):
        seat_svc = SeatService()
        booking_svc = BookingService()

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat1"].id, test_setup["user1"].id)

        # Initial confirm
        booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            promo_code="IDEMP10",
            idempotency_key="key-single-rewards-004",
        )

        # Re-query user and promo
        u = db_session.get(User, test_setup["user1"].id)
        p = db_session.get(PromoCode, test_setup["promo"].id)

        expected_cashback = 1.80  # 2% of 90.00
        assert float(u.reward_balance) == expected_cashback
        assert p.used_count == 1

        # Duplicate replay
        booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            promo_code="IDEMP10",
            idempotency_key="key-single-rewards-004",
        )

        db_session.refresh(u)
        db_session.refresh(p)

        # Balances & promo usages must NOT increase
        assert float(u.reward_balance) == expected_cashback
        assert p.used_count == 1

        # Exactly 1 ticket and 1 reward transaction
        t_count = Ticket.query.filter(Ticket.booking_id.isnot(None)).count()
        r_count = RewardTransaction.query.filter(RewardTransaction.user_id == u.id).count()
        assert t_count == 1
        assert r_count == 1

    # 5. Different key creates a legitimate separate booking
    def test_different_key_creates_separate_booking(self, test_setup):
        seat_svc = SeatService()
        booking_svc = BookingService()

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat1"].id, test_setup["user1"].id)
        res1 = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            idempotency_key="key-order-1",
        )
        assert res1["success"] is True

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat2"].id, test_setup["user1"].id)
        res2 = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            idempotency_key="key-order-2",
        )
        assert res2["success"] is True
        assert res1["data"]["booking_id"] != res2["data"]["booking_id"]

    # 6. Missing key remains compatible with non-idempotent flow
    def test_missing_key_compatible(self, test_setup):
        seat_svc = SeatService()
        booking_svc = BookingService()

        seat_svc.hold_seat(test_setup["event"].id, test_setup["seat3"].id, test_setup["user1"].id)
        res = booking_svc.confirm_booking(
            user_id=test_setup["user1"].id,
            event_id=test_setup["event"].id,
            idempotency_key=None,
        )
        assert res["success"] is True
        assert res["status"] == 201
