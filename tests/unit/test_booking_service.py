# tests/unit/test_booking_service.py
#
# Unit tests for BookingService covering pricing calculations, seat/GA flows,
# promo discounts, 2% cashback rewards, transactions, and cancellations.
# WHY: Booking is the central revenue-generating workflow in SeatMeUp.
# We must ensure financial integrity:
#   1. Pricing: Base Price + Seats + Addons - Promo Discount.
#   2. Rewards: Exact 2% cashback credited to User reward ledger on confirmation.
#   3. Hold Consumption: Active holds become 'consumed'.
#   4. Cancellation: Reverses 2% cashback ledger, marks booking 'cancelled', invalidates ticket.

import pytest
from datetime import date, timedelta, time
from models.seat import Seat
from models.seat_hold import SeatHold
from models.event_addon import EventAddon
from models.promo_code import PromoCode
from models.booking import Booking
from models.ticket import Ticket
from models.event import Event
from models.user import User
from Services.booking_service import BookingService
from Services.seat_service import SeatService


@pytest.mark.unit
class TestBookingService:
    @pytest.fixture(autouse=True)
    def setup_service(self, db_session, customer_user, category, venue, event):
        self.booking_service = BookingService()
        self.seat_service = SeatService()
        self.db = db_session
        self.customer = customer_user
        self.user_id = customer_user.id
        self.venue_id = venue.id
        self.category_id = category.id
        self.event = event
        self.event_id = event.id

    def test_seated_booking_with_addons_and_percentage_promo(self):
        """WHY: Validates complex multi-item seated pricing: Seats + Addon - Promo (20%) + 2% Cashback."""
        # 1. Create Seat and hold it
        seat = Seat(venue_id=self.venue_id, seat_number="S-1", section_name="VIP", price=150.00, is_active=True)
        self.db.add(seat)
        self.db.commit()

        hold_res = self.seat_service.hold_seat(event_id=self.event_id, seat_id=seat.id, user_id=self.user_id)
        assert hold_res["success"] is True

        # 2. Add-on ($50) and Promo (20% off)
        addon = EventAddon(event_id=self.event_id, name="VIP Pass", price=50.00, available_quantity=10, is_active=True)
        promo = PromoCode(code="DISCOUNT20", discount_type="percentage", discount_value=20.00, minimum_booking_amount=100.00, is_active=True)
        self.db.add_all([addon, promo])
        self.db.commit()

        # 3. Confirm booking: ($150 seat + $50 addon = $200) - 20% ($40) = $160.00 Total
        res = self.booking_service.confirm_booking(
            user_id=self.user_id,
            event_id=self.event_id,
            selected_addons={str(addon.id): 1},
            promo_code="DISCOUNT20",
        )
        assert res["success"] is True
        b_data = res["data"]

        assert b_data["total_amount"] == 160.00
        assert b_data["discount_amount"] == 40.00
        assert b_data["cashback_amount"] == 3.20  # 2% of $160.00

        # Check user reward balance in DB
        u = self.db.get(User, self.user_id)
        assert float(u.reward_balance) == 3.20

        # Verify hold is consumed
        hold = self.db.query(SeatHold).filter_by(event_id=self.event_id, seat_id=seat.id).first()
        assert hold.status == "consumed"

    def test_general_admission_booking_without_seats(self):
        """WHY: General admission events compute price as quantity * base_price and reward 2% cashback."""
        ga_event = Event(
            title="Open Festival",
            category_id=self.category_id,
            venue_id=self.venue_id,
            created_by=self.user_id,
            event_date=date.today() + timedelta(days=5),
            start_time=time(12, 0, 0),
            base_price=40.00,
            booking_open=True,
            requires_seats=False,
            status="published",
        )
        self.db.add(ga_event)
        self.db.commit()

        # 3 tickets @ $40.00 = $120.00
        res = self.booking_service.confirm_booking(user_id=self.user_id, event_id=ga_event.id, quantity=3)
        assert res["success"] is True
        assert res["data"]["total_amount"] == 120.00
        assert res["data"]["cashback_amount"] == 2.40

    def test_booking_rejected_when_no_active_seat_holds(self):
        """WHY: Seated event booking must be rejected with 400 when user has not placed a valid seat hold."""
        res = self.booking_service.confirm_booking(user_id=self.user_id, event_id=self.event_id)
        assert res["success"] is False
        assert res["status"] == 400
        assert "No active seat holds found" in res["message"]

    def test_cancellation_reverses_cashback_and_marks_ticket_cancelled(self):
        """WHY: Booking cancellation reverses 2% cashback from user balance and invalidates the ticket."""
        ga_event = Event(
            title="Concert", category_id=self.category_id, venue_id=self.venue_id,
            created_by=self.user_id,
            event_date=date.today()+timedelta(days=2), start_time=time(20, 0, 0), base_price=100.0,
            booking_open=True, requires_seats=False, status="published"
        )
        self.db.add(ga_event)
        self.db.commit()

        b_res = self.booking_service.confirm_booking(user_id=self.user_id, event_id=ga_event.id, quantity=1)
        booking_id = b_res["data"]["booking_id"]

        # User balance should be $2.00
        u = self.db.get(User, self.user_id)
        assert float(u.reward_balance) == 2.00

        # Cancel booking
        c_res = self.booking_service.cancel_booking(booking_id=booking_id, user_id=self.user_id)
        assert c_res["success"] is True

        # Check booking status
        b_after = self.db.get(Booking, booking_id)
        assert b_after.status == "cancelled"
        assert b_after.cancelled_at is not None

        # Check ticket status
        ticket = self.db.query(Ticket).filter_by(booking_id=booking_id).first()
        assert ticket.ticket_status == "cancelled"

        # Check reward reversal
        u_after = self.db.get(User, self.user_id)
        assert float(u_after.reward_balance) == 0.00
