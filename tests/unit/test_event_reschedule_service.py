# tests/unit/test_event_reschedule_service.py
#
# Unit tests for EventRescheduleService.
# WHY: Rescheduling an event is a sensitive administrative action:
#   1. Admin must confirm their password to prevent unauthorized modifications.
#   2. New event date must be in the future.
#   3. Creates an audit record in `event_reschedules`.
#   4. Dispatches in-app notifications and emails to all affected ticket holders.

import pytest
from datetime import date, timedelta, time
from werkzeug.security import generate_password_hash
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.event_reschedule import EventReschedule
from Services.event_reschedule_service import EventRescheduleService


@pytest.mark.unit
class TestEventRescheduleService:
    @pytest.fixture(autouse=True)
    def setup_service(self, db_session):
        self.reschedule_service = EventRescheduleService()
        self.db = db_session

        # Seed admin and customer
        self.admin = User(
            name="Admin User",
            email="admin_resched@test.com",
            password_hash=generate_password_hash("secret123"),
            role="admin",
            is_active=True,
        )
        self.cat = Category(name="Rock")
        self.venue = Venue(name="Arena", address="100 St", capacity=100)

        self.db.add_all([self.admin, self.cat, self.venue])
        self.db.commit()

        self.event = Event(
            title="Rock Festival",
            category_id=self.cat.id,
            venue_id=self.venue.id,
            created_by=self.admin.id,
            event_date=date.today() + timedelta(days=7),
            start_time=time(18, 0, 0),
            base_price=50.00,
            status="published",
        )
        self.db.add(self.event)
        self.db.commit()

    def test_reschedule_success_with_valid_password(self):
        """WHY: Valid admin password and future date updates event, logs audit, and returns 200."""
        new_date = str(date.today() + timedelta(days=21))
        res = self.reschedule_service.reschedule_event(
            event_id=self.event.id,
            admin_id=self.admin.id,
            new_event_date=new_date,
            new_start_time="20:00",
            reason="Artist illness",
            password="secret123",
        )
        assert res["success"] is True
        assert res["status"] == 200

        # Verify Event in DB
        ev_after = self.db.get(Event, self.event.id)
        assert str(ev_after.event_date) == new_date
        assert str(ev_after.start_time) == "20:00:00"

        # Verify EventReschedule record
        audit = self.db.query(EventReschedule).filter_by(event_id=self.event.id).first()
        assert audit is not None
        assert audit.admin_id == self.admin.id
        assert audit.reason == "Artist illness"

    def test_reschedule_wrong_password_rejected(self):
        """WHY: Incorrect admin password must reject the rescheduling with 401."""
        res = self.reschedule_service.reschedule_event(
            event_id=self.event.id,
            admin_id=self.admin.id,
            new_event_date=str(date.today() + timedelta(days=21)),
            new_start_time="20:00",
            reason="Weather",
            password="WRONG_PASSWORD",
        )
        assert res["success"] is False
        assert res["status"] == 401
        assert "Incorrect admin password" in res["message"]

    def test_reschedule_past_date_rejected(self):
        """WHY: Rescheduling to a date in the past is invalid and blocked with 400."""
        past_date = str(date.today() - timedelta(days=2))
        res = self.reschedule_service.reschedule_event(
            event_id=self.event.id,
            admin_id=self.admin.id,
            new_event_date=past_date,
            new_start_time="20:00",
            reason="Reschedule",
            password="secret123",
        )
        assert res["success"] is False
        assert res["status"] == 400
        assert "past" in res["message"]
