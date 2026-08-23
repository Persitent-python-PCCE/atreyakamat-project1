# tests/models/test_booking_model.py
#
# SQLAlchemy Model test for Booking model.
# WHY: Verifies Booking model fields and status defaults ('confirmed' or 'pending').

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.booking import Booking


@pytest.mark.model
class TestBookingModel:
    def test_booking_model_fields_and_defaults(self, db_session):
        """WHY: Booking model defaults total_amount to 0.00 and status to 'pending'."""
        user = User(name="Buyer", email="b@test.com", password_hash="hash")
        cat = Category(name="Pop")
        ven = Venue(name="Arena", address="100 St")
        db_session.add_all([user, cat, ven])
        db_session.commit()

        ev = Event(category_id=cat.id, venue_id=ven.id, created_by=user.id, title="Pop Night", event_date=date.today()+timedelta(days=1), start_time=time(19, 0, 0))
        db_session.add(ev)
        db_session.commit()

        bk = Booking(user_id=user.id, event_id=ev.id, booking_reference="SMU-TEST1234")
        db_session.add(bk)
        db_session.commit()

        assert bk.id is not None
        assert bk.booking_reference == "SMU-TEST1234"
        assert float(bk.total_amount) == 0.00
        assert bk.status == "pending"
