# DAO/event_reschedule_dao.py
#
# EventRescheduleDAO — Data Access Object for the `event_reschedules` table.
# Each row records one admin-approved change of an event's date/time.
#
# This DAO does NOT perform the reschedule workflow itself (erasing the old
# date on the Event, sending notifications, password confirmation, etc.).
# Those are all Service-layer concerns.

from app import db
from models.event_reschedule import EventReschedule


class EventRescheduleDAO:
    """Database operations for the EventReschedule model."""

    def create_reschedule(
        self, reschedule: EventReschedule
    ) -> EventReschedule:
        """Insert a new reschedule record row."""
        try:
            db.session.add(reschedule)
            db.session.commit()
            return reschedule
        except Exception:
            db.session.rollback()
            raise

    def get_reschedule_by_id(self, reschedule_id: int) -> EventReschedule | None:
        """Load one reschedule record by its primary key."""
        return db.session.get(EventReschedule, reschedule_id)

    def get_reschedules_by_event(self, event_id: int) -> list[EventReschedule]:
        """Return every reschedule record for a given event (audit history)."""
        return EventReschedule.query.filter_by(event_id=event_id).all()

    def get_reschedules_by_admin(self, admin_id: int) -> list[EventReschedule]:
        """Return every reschedule performed by a given admin user."""
        return EventReschedule.query.filter_by(admin_id=admin_id).all()

    def update_reschedule(
        self, reschedule: EventReschedule
    ) -> EventReschedule:
        """Commit changes the Service already applied to `reschedule`."""
        try:
            db.session.commit()
            return reschedule
        except Exception:
            db.session.rollback()
            raise

    def delete_reschedule(self, reschedule: EventReschedule) -> bool:
        """Delete the given reschedule row. Returns True on success."""
        try:
            db.session.delete(reschedule)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
