# tests/models/test_event_model.py
#
# SQLAlchemy Model test for Event model.
# WHY: Verifies Event model defaults (status='unpublished', booking_open=True, requires_seats=True).

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event


@pytest.mark.model
class TestEventModel:
    def test_event_model_fields_and_defaults(self, db_session):
        """WHY: Verifies Event model creation with category, venue, and status defaults."""
        user = User(name="Creator", email="creator@event.com", password_hash="pw")
        cat = Category(name="Indie Music")
        ven = Venue(name="City Arena", address="1 Main St")
        db_session.add_all([user, cat, ven])
        db_session.commit()

        ev = Event(
            title="Indie Rock Night",
            category_id=cat.id,
            venue_id=ven.id,
            created_by=user.id,
            event_date=date.today() + timedelta(days=7),
            start_time=time(19, 0, 0),
            base_price=45.00,
        )
        db_session.add(ev)
        db_session.commit()

        assert ev.id is not None
        assert ev.status == "unpublished"
        assert ev.booking_open is True
        assert ev.requires_seats is True
