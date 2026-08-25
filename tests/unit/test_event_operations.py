# tests/unit/test_event_operations.py
#
# Dedicated test suite for Event Operations Dashboard & Health Score.
# WHY: Verifies that single event operations metrics, sales vs live occupancy,
# no-show rates, active holds, expired holds today, and the transparent 0-100
# health score calculation are correctly computed from real database values.

import pytest
from datetime import date, timedelta, time, datetime
from models.user import User
from models.category import Category
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.booking import Booking
from models.booking_item import BookingItem
from models.ticket import Ticket
from models.ticket_verification import TicketVerification
from models.seat_hold import SeatHold
from DAO.analytics_dao import AnalyticsDAO
from Services.analytics_service import AnalyticsService


@pytest.mark.unit
class TestEventOperations:
    @pytest.fixture
    def ops_setup(self, db_session):
        admin = User(name="Ops Admin", email="opsadmin@seatmeup.com", password_hash="pw", role="admin")
        customer1 = User(name="Ops Customer 1", email="opscust1@example.com", password_hash="pw", role="customer")
        customer2 = User(name="Ops Customer 2", email="opscust2@example.com", password_hash="pw", role="customer")
        cat = Category(name="Ops Festival")
        ven = Venue(name="Ops Arena", address="500 Arena Blvd", venue_type="seated", capacity=10)
        db_session.add_all([admin, customer1, customer2, cat, ven])
        db_session.commit()

        # Add 10 seats
        seats = [
            Seat(venue_id=ven.id, seat_number=f"S{i}", section_name="Main", price=100.00, is_active=True)
            for i in range(1, 11)
        ]
        db_session.add_all(seats)
        db_session.commit()

        # Event: 10 capacity, 4 sold, 2 checked in, 1 active hold, 1 expired hold, 1 cancellation
        ev = Event(
            title="Goa Music Nights",
            category_id=cat.id,
            venue_id=ven.id,
            created_by=admin.id,
            event_date=date.today() + timedelta(days=5),
            start_time=time(20, 0),
            base_price=100.00,
            status="published",
            booking_open=True,
            requires_seats=True,
        )
        db_session.add(ev)
        db_session.commit()

        # Booking 1: Customer 1 books 2 seats (S1, S2) -> Confirmed, 1 ticket checked in
        b1 = Booking(
            user_id=customer1.id,
            event_id=ev.id,
            booking_reference="BK-OPS-001",
            total_amount=200.00,
            status="confirmed",
            booked_at=datetime.utcnow(),
        )
        db_session.add(b1)
        db_session.flush()

        item1 = BookingItem(booking_id=b1.id, seat_id=seats[0].id, item_type="ticket", quantity=1, unit_price=100.00, total_price=100.00)
        item2 = BookingItem(booking_id=b1.id, seat_id=seats[1].id, item_type="ticket", quantity=1, unit_price=100.00, total_price=100.00)
        tkt1 = Ticket(booking_id=b1.id, ticket_token="TKT-OPS-001", ticket_status="used", qr_data="SEATMEUP:001", issued_at=datetime.utcnow())
        db_session.add_all([item1, item2, tkt1])
        db_session.flush()

        scan1 = TicketVerification(
            ticket_id=tkt1.id,
            verification_status="success",
            verified_at=datetime.utcnow(),
        )
        db_session.add(scan1)

        # Booking 2: Customer 2 books 2 seats (S3, S4) -> Confirmed, ticket valid (not scanned)
        b2 = Booking(
            user_id=customer2.id,
            event_id=ev.id,
            booking_reference="BK-OPS-002",
            total_amount=200.00,
            status="confirmed",
            booked_at=datetime.utcnow(),
        )
        db_session.add(b2)
        db_session.flush()

        item3 = BookingItem(booking_id=b2.id, seat_id=seats[2].id, item_type="ticket", quantity=1, unit_price=100.00, total_price=100.00)
        item4 = BookingItem(booking_id=b2.id, seat_id=seats[3].id, item_type="ticket", quantity=1, unit_price=100.00, total_price=100.00)
        tkt2 = Ticket(booking_id=b2.id, ticket_token="TKT-OPS-002", ticket_status="valid", qr_data="SEATMEUP:002", issued_at=datetime.utcnow())
        db_session.add_all([item3, item4, tkt2])

        # Booking 3: Cancelled booking
        b3 = Booking(
            user_id=customer2.id,
            event_id=ev.id,
            booking_reference="BK-OPS-003",
            total_amount=100.00,
            status="cancelled",
            booked_at=datetime.utcnow() - timedelta(days=1),
            cancelled_at=datetime.utcnow(),
        )
        db_session.add(b3)

        # Active hold on S5
        hold_active = SeatHold(
            event_id=ev.id,
            seat_id=seats[4].id,
            user_id=customer1.id,
            hold_token="HOLD-ACTIVE-1",
            status="active",
            held_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=1),
        )
        # Expired hold on S6
        hold_expired = SeatHold(
            event_id=ev.id,
            seat_id=seats[5].id,
            user_id=customer2.id,
            hold_token="HOLD-EXP-1",
            status="expired",
            held_at=datetime.utcnow() - timedelta(hours=2),
            expires_at=datetime.utcnow() - timedelta(hours=2, minutes=-1),
        )
        db_session.add_all([hold_active, hold_expired])
        db_session.commit()

        return {
            "admin": admin,
            "event": ev,
            "venue": ven,
        }

    def test_event_operations_metrics_calculation(self, ops_setup):
        svc = AnalyticsService()
        res = svc.get_event_operations(ops_setup["event"].id)
        assert res["success"] is True
        data = res["data"]

        # Capacity: 10 seats
        assert data["capacity"] == 10
        # Tickets Sold: 4 (2 in B1 + 2 in B2)
        assert data["tickets_sold"] == 4
        # Checked In: 1 (TKT-OPS-001 with 'used' status)
        assert data["checked_in"] == 1
        # Remaining: 10 - 4 = 6
        assert data["remaining_capacity"] == 6

        # Sales Occupancy: 4 / 10 = 40.0%
        assert data["sales_occupancy"] == 40.0
        # Live Occupancy: 1 / 10 = 10.0%
        assert data["live_occupancy"] == 10.0

        # No-shows: 4 sold - 1 checked in = 3
        assert data["no_shows"] == 3
        # No-show rate: 3 / 4 = 75.0%
        assert data["no_show_rate"] == 75.0

        # Holds
        assert data["active_holds"] == 1
        assert data["expired_holds_today"] == 1
        assert data["cancellations"] == 1

        # Revenue
        assert data["revenue"] == 400.00
        assert data["last_scan"] is not None

        # Health Score & Categories
        assert 0 <= data["health_score"] <= 100
        assert data["health_category"] in ("Excellent", "Healthy", "Needs Attention", "At Risk")
        assert len(data["health_reasons"]) >= 2

        # Timeline
        assert len(data["timeline"]) >= 2
        actions = [item["action"] for item in data["timeline"]]
        assert "Ticket verified" in actions
        assert "Booking created" in actions

    def test_event_operations_nonexistent_returns_404(self, db_session):
        svc = AnalyticsService()
        res = svc.get_event_operations(99999)
        assert res["success"] is False
        assert res["status"] == 404
