# DAO/event_dao.py
#
# EventDAO — Data Access Object for the `events` table.
# An event is a scheduled show/occasion that customers can book.
#
# This DAO has a few extra retrieval methods (upcoming, by category, search)
# because those are common lookups for the events listing page.

from datetime import datetime

from app import db
from models.event import Event


class EventDAO:
    """Database operations for the Event model."""

    # ---------------- CREATE ----------------
    def create_event(self, event: Event) -> Event:
        """Insert a new event row."""
        try:
            db.session.add(event)
            db.session.commit()
            return event
        except Exception:
            db.session.rollback()
            raise

    # ---------------- READ ----------------
    def get_event_by_id(self, event_id: int) -> Event | None:
        """Load one event by its primary key, or None if not found."""
        return db.session.get(Event, event_id)

    def get_all_events(self) -> list[Event]:
        """Return every event in the database."""
        return Event.query.all()

    def get_upcoming_events(self) -> list[Event]:
        """Return events whose event_date is in the future.

        We compare against the current UTC datetime. .filter() lets us write
        a column-against-expression condition (unlike filter_by which is
        only equality). We order by event_date so the soonest ones come first.
        """
        now = datetime.utcnow()
        return (
            Event.query
            .filter(Event.event_date >= now)
            .order_by(Event.event_date.asc())
            .all()
        )

    def get_events_by_category(self, category_id: int) -> list[Event]:
        """Return all events that belong to a given category id."""
        return Event.query.filter_by(category_id=category_id).all()

    def search_events(self, search_term: str) -> list[Event]:
        """Return events whose title contains the search term.

        .ilike(...) is a case-insensitive LIKE in SQLAlchemy.
        The % wildcards mean "any characters before/after the search term".
        """
        if not search_term:
            return []
        pattern = f"%{search_term}%"
        return Event.query.filter(Event.title.ilike(pattern)).all()

    # ---------------- UPDATE ----------------
    def update_event(self, event: Event) -> Event:
        """Commit any changes the Service already applied to `event`."""
        try:
            db.session.commit()
            return event
        except Exception:
            db.session.rollback()
            raise

    # ---------------- DELETE ----------------
    def delete_event(self, event: Event) -> bool:
        """Delete the given event row. Returns True on success."""
        try:
            db.session.delete(event)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
