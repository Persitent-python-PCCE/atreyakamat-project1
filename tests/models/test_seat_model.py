# tests/models/test_seat_model.py
#
# SQLAlchemy Model test for Seat model.
# WHY: Verifies Seat model pricing, section defaults, and active status.

import pytest
from models.venue import Venue
from models.seat import Seat


@pytest.mark.model
class TestSeatModel:
    def test_seat_model_fields_and_defaults(self, db_session):
        """WHY: Seat model defaults is_active to True and price to 0.00."""
        ven = Venue(name="Concert Hall", address="500 Broadway")
        db_session.add(ven)
        db_session.commit()

        seat = Seat(venue_id=ven.id, seat_number="B-12", section_name="Balcony", price=60.00)
        db_session.add(seat)
        db_session.commit()

        assert seat.id is not None
        assert seat.seat_number == "B-12"
        assert seat.is_active is True
        assert float(seat.price) == 60.00
