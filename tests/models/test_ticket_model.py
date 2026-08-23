# tests/models/test_ticket_model.py
#
# SQLAlchemy Model test for Ticket model.
# WHY: Verifies Ticket model fields and default status ('valid').

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.booking import Booking
from models.ticket import Ticket


@pytest.mark.model
class TestTicketModel:
    def test_ticket_model_fields_and_defaults(self, db_session):
        """WHY: Ticket model defaults ticket_status to 'valid' and associates with Booking."""
        user = User(name="Buyer", email="ticketbuyer@test.com", password_hash="hash")
        cat = Category(name="Rock")
        ven = Venue(name="Arena", address="100 St")
        db_session.add_all([user, cat, ven])
        db_session.commit()

        ev = Event(category_id=cat.id, venue_id=ven.id, created_by=user.id, title="Rock", event_date=date.today()+timedelta(days=1), start_time=time(19, 0, 0))
        db_session.add(ev)
        db_session.commit()

        bk = Booking(user_id=user.id, event_id=ev.id, booking_reference="SMU-TKTTEST")
        db_session.add(bk)
        db_session.commit()

        tkt = Ticket(booking_id=bk.id, ticket_token="TKT-SAMPLE12345")
        db_session.add(tkt)
        db_session.commit()

        assert tkt.id is not None
        assert tkt.ticket_token == "TKT-SAMPLE12345"
        assert tkt.ticket_status == "valid"
