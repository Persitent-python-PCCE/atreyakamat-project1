# tests/unit/test_serializers.py
#
# Pure unit tests for serializers and data sanitization.
# WHY: Serializers convert SQLAlchemy model instances into JSON dictionaries.
# CRITICAL SECURITY GUARD: `user_to_dict` must NEVER include `password_hash` in its payload.

import pytest
from datetime import datetime, date, time
from decimal import Decimal
from models.user import User
from models.event import Event
from api.serializers import _ser, user_to_dict, event_to_dict


@pytest.mark.unit
class TestSerializers:
    def test_primitive_serializer_helper(self):
        """WHY: _ser helper correctly handles diverse Python data types (dates, times, decimals)."""
        d = date(2026, 8, 23)
        assert _ser(d) == "2026-08-23"

        t = time(14, 30, 0)
        assert _ser(t) == "14:30:00"

        dt = datetime(2026, 8, 23, 14, 30, 0)
        assert _ser(dt) == "2026-08-23T14:30:00"

        dec = Decimal("45.50")
        assert _ser(dec) == 45.50

        assert _ser(None) is None
        assert _ser("already_string") == "already_string"

    def test_user_serializer_never_exposes_password_hash(self):
        """WHY: CRITICAL SECURITY TEST: Ensure user_to_dict never includes password_hash in JSON responses."""
        u = User(
            id=10,
            name="John Doe",
            email="john@example.com",
            password_hash="pbkdf2:sha256:secret_hash_value",
            role="customer",
            reward_balance=Decimal("15.50"),
            is_active=True,
        )
        d = user_to_dict(u)

        assert "password_hash" not in d
        assert "password" not in d
        assert d["id"] == 10
        assert d["email"] == "john@example.com"
        assert d["reward_balance"] == 15.50

    def test_event_serializer_fields(self):
        """WHY: event_to_dict serializes financial and date information accurately."""
        ev = Event(
            id=1,
            title="Concert",
            category_id=2,
            venue_id=3,
            event_date=date(2026, 9, 1),
            start_time=time(19, 0, 0),
            base_price=Decimal("80.00"),
            status="published",
            booking_open=True,
            requires_seats=True,
        )
        d = event_to_dict(ev)

        assert d["id"] == 1
        assert d["title"] == "Concert"
        assert d["base_price"] == 80.00
        assert d["event_date"] == "2026-09-01"
        assert d["start_time"] == "19:00:00"
        assert d["status"] == "published"
