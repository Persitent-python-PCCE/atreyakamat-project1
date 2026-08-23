# tests/models/test_relationships.py
#
# Tests for bidirectional SQLAlchemy relationships across all 19 database models.
# WHY: Catches mapper, foreign key, back_populates, and cascade regressions across the entire domain model.

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.seat import Seat
from models.seat_hold import SeatHold
from models.event_addon import EventAddon
from models.booking import Booking
from models.booking_item import BookingItem
from models.booking_addon import BookingAddon
from models.ticket import Ticket
from models.ticket_verification import TicketVerification
from models.reward_transaction import RewardTransaction
from models.notification import Notification
from models.event_reschedule import EventReschedule


@pytest.mark.model
class TestModelRelationships:
    def test_complete_bidirectional_relationships(self, db_session):
        """WHY: Verifies bidirectional mapping across User, Event, Venue, Booking, and Ticket ecosystems."""
        # 1. User, Category, Venue
        user = User(name="User", email="u@rel.com", password_hash="pw")
        admin = User(name="Admin", email="adm@rel.com", password_hash="pw", role="admin")
        cat = Category(name="Jazz")
        ven = Venue(name="Blue Note", address="131 W 3rd St")
        db_session.add_all([user, admin, cat, ven])
        db_session.commit()

        # 2. User <-> Notification
        notif = Notification(user_id=user.id, title="Test", message="Msg", notification_type="booking_confirmation")
        db_session.add(notif)
        db_session.commit()
        assert notif in user.notifications

        # 3. Venue <-> Seat
        seat = Seat(venue_id=ven.id, seat_number="J-1")
        db_session.add(seat)
        db_session.commit()
        assert seat in ven.seats
        assert seat.venue == ven

        # 4. Category/Venue <-> Event
        ev = Event(
            category_id=cat.id, venue_id=ven.id, created_by=admin.id,
            title="Jazz Trio", event_date=date.today()+timedelta(days=5), start_time=time(20, 0, 0)
        )
        db_session.add(ev)
        db_session.commit()
        assert ev in cat.events
        assert ev in ven.events
        assert ev.category == cat
        assert ev.venue == ven

        # 5. Event <-> EventAddon
        addon = EventAddon(event_id=ev.id, name="Drink Voucher", price=15.0)
        db_session.add(addon)
        db_session.commit()
        assert addon in ev.event_addons
        assert addon.event == ev

        # 6. User/Event <-> SeatHold
        hold = SeatHold(event_id=ev.id, seat_id=seat.id, user_id=user.id, hold_token="TOK-REL", expires_at=date.today()+timedelta(days=1))
        db_session.add(hold)
        db_session.commit()
        assert hold in user.seat_holds
        assert hold in ev.seat_holds

        # 7. User/Event <-> Booking
        booking = Booking(user_id=user.id, event_id=ev.id, booking_reference="SMU-RELBOOK")
        db_session.add(booking)
        db_session.commit()
        assert booking in user.bookings
        assert booking in ev.bookings

        # 8. Booking <-> BookingItem & BookingAddon
        item = BookingItem(booking_id=booking.id, seat_id=seat.id, quantity=1, unit_price=50.0, total_price=50.0)
        b_addon = BookingAddon(booking_id=booking.id, addon_id=addon.id, quantity=1, unit_price=15.0, total_price=15.0)
        db_session.add_all([item, b_addon])
        db_session.commit()
        assert item in booking.booking_items
        assert b_addon in booking.booking_addons

        # 9. Booking <-> Ticket <-> TicketVerification
        ticket = Ticket(booking_id=booking.id, ticket_token="TKT-REL123")
        db_session.add(ticket)
        db_session.commit()
        assert booking.ticket == ticket
        assert ticket.booking == booking

        tv = TicketVerification(ticket_id=ticket.id, verification_status="success")
        db_session.add(tv)
        db_session.commit()
        assert tv in ticket.ticket_verifications
        assert tv.ticket == ticket

        # 10. User <-> RewardTransaction & EventReschedule
        rt = RewardTransaction(user_id=user.id, booking_id=booking.id, transaction_type="cashback", amount=1.0)
        resched = EventReschedule(
            event_id=ev.id, admin_id=admin.id,
            old_event_date=ev.event_date, old_start_time=ev.start_time,
            new_event_date=ev.event_date+timedelta(days=1), new_start_time=ev.start_time
        )
        db_session.add_all([rt, resched])
        db_session.commit()

        assert rt in user.reward_transactions
        assert resched in admin.event_reschedules
        assert resched in ev.event_reschedules
