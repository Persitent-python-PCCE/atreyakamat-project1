# tests/models/test_venue_model.py
#
# SQLAlchemy Model test for Venue model.
# WHY: Verifies Venue model fields, capacity constraints, and venue_type defaults.

import pytest
from models.venue import Venue


@pytest.mark.model
class TestVenueModel:
    def test_venue_model_fields_and_defaults(self, db_session):
        """WHY: Venue model defaults venue_type to 'seated' and capacity to 0."""
        ven = Venue(name="Acoustic Lounge", address="22 Jazz Way")
        db_session.add(ven)
        db_session.commit()

        assert ven.id is not None
        assert ven.venue_type == "seated"
        assert ven.capacity == 0
        assert ven.created_at is not None
