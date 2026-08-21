# DAO/event_addon_dao.py
#
# EventAddonDAO — Data Access Object for the `event_addons` table.
# An add-on is an optional extra for an event (e.g. VIP parking).

from app import db
from models.event_addon import EventAddon


class EventAddonDAO:
    """Database operations for the EventAddon model."""

    def create_addon(self, addon: EventAddon) -> EventAddon:
        """Insert a new event add-on row."""
        try:
            db.session.add(addon)
            db.session.commit()
            return addon
        except Exception:
            db.session.rollback()
            raise

    def get_addon_by_id(self, addon_id: int) -> EventAddon | None:
        """Load one add-on by its primary key."""
        return db.session.get(EventAddon, addon_id)

    def get_addons_by_event(self, event_id: int) -> list[EventAddon]:
        """Return every add-on attached to the given event."""
        return EventAddon.query.filter_by(event_id=event_id).all()

    def get_all_addons(self) -> list[EventAddon]:
        """Return every add-on in the database."""
        return EventAddon.query.all()

    def update_addon(self, addon: EventAddon) -> EventAddon:
        """Commit changes the Service already applied to `addon`."""
        try:
            db.session.commit()
            return addon
        except Exception:
            db.session.rollback()
            raise

    def delete_addon(self, addon: EventAddon) -> bool:
        """Delete the given add-on row. Returns True on success."""
        try:
            db.session.delete(addon)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
