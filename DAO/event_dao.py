# DAO/event_dao.py
#
# EventDAO — Data Access Object for the `events` table.
# An event is a scheduled show/occasion that customers can book.

from datetime import datetime

from app import db
from models.event import Event
from models.category import Category


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
        """Return every event in the database (Admin/internal use)."""
        return Event.query.all()

    def get_published_events(self) -> list[Event]:
        """Return only published events for public listing."""
        return Event.query.filter_by(status="published").all()

    def get_upcoming_events(self) -> list[Event]:
        """Return published events whose event_date is in the future or today."""
        now = datetime.utcnow()
        return (
            Event.query
            .filter(Event.status == "published", Event.event_date >= now.date())
            .order_by(Event.event_date.asc())
            .all()
        )

    def get_events_by_category(self, category_id: int) -> list[Event]:
        """Return published events that belong to a given category id."""
        return Event.query.filter_by(category_id=category_id, status="published").all()

    def get_events_by_category_name(self, category_name: str) -> list[Event]:
        """Return published events that belong to a category name."""
        if not category_name or not category_name.strip():
            return []
        return (
            Event.query
            .join(Event.category)
            .filter(Category.name.ilike(category_name.strip()), Event.status == "published")
            .all()
        )

    def search_events(self, search_term: str) -> list[Event]:
        """Return published events whose title, description, or category matches search term."""
        if not search_term or not search_term.strip():
            return []
        pattern = f"%{search_term.strip()}%"
        return (
            Event.query
            .outerjoin(Event.category)
            .filter(
                Event.status == "published",
                (
                    Event.title.ilike(pattern) |
                    Event.description.ilike(pattern) |
                    Category.name.ilike(pattern)
                )
            )
            .all()
        )

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
