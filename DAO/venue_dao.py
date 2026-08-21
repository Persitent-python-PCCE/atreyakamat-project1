# DAO/venue_dao.py
#
# VenueDAO — Data Access Object for the `venues` table.
# A venue is a physical place (stadium, hall) where events happen.

from app import db
from models.venue import Venue


class VenueDAO:
    """Database operations for the Venue model."""

    def create_venue(self, venue: Venue) -> Venue:
        """Insert a new venue row."""
        try:
            db.session.add(venue)
            db.session.commit()
            return venue
        except Exception:
            db.session.rollback()
            raise

    def get_venue_by_id(self, venue_id: int) -> Venue | None:
        """Load one venue by its primary key."""
        return db.session.get(Venue, venue_id)

    def get_all_venues(self) -> list[Venue]:
        """Return every venue in the database."""
        return Venue.query.all()

    def update_venue(self, venue: Venue) -> Venue:
        """Commit any changes the Service already applied to `venue`."""
        try:
            db.session.commit()
            return venue
        except Exception:
            db.session.rollback()
            raise

    def delete_venue(self, venue: Venue) -> bool:
        """Delete the given venue row. Returns True on success."""
        try:
            db.session.delete(venue)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
