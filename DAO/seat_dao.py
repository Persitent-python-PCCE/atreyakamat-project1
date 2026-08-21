# DAO/seat_dao.py
#
# SeatDAO — Data Access Object for the `seats` table.
# A seat belongs to a Venue (per models/seat.py — venue_id FK).
#
# NOTE on "available seats":
# In the real SeatMeUp design, whether a seat is available depends on
# active SeatHolds and confirmed BookingItems. Computing that is a
# cross-model business decision and belongs in the Service layer.
# So get_available_seats() here returns only seats that are active
# (is_active = True) for that venue — the Service can further filter
# out held/sold ones later.

from app import db
from models.seat import Seat


class SeatDAO:
    """Database operations for the Seat model."""

    def create_seat(self, seat: Seat) -> Seat:
        """Insert a new seat row."""
        try:
            db.session.add(seat)
            db.session.commit()
            return seat
        except Exception:
            db.session.rollback()
            raise

    def create_seats_bulk(self, seats: list[Seat]) -> list[Seat]:
        """Insert many seats in one transaction.

        Useful when an admin creates a whole seat layout for a venue at once.
        Either ALL succeed or ALL roll back — there is no partial insert.
        """
        try:
            for s in seats:
                db.session.add(s)
            db.session.commit()
            return seats
        except Exception:
            db.session.rollback()
            raise

    def get_seat_by_id(self, seat_id: int) -> Seat | None:
        """Load one seat by its primary key."""
        return db.session.get(Seat, seat_id)

    def get_seats_by_venue(self, venue_id: int) -> list[Seat]:
        """Return every seat that belongs to the given venue."""
        return Seat.query.filter_by(venue_id=venue_id).all()

    def get_available_seats(self, venue_id: int) -> list[Seat]:
        """Return active seats of a venue (is_active = True).

        This is a basic availability filter — the full "not held, not sold"
        logic belongs to the Service, which can combine this with SeatHoldDAO
        and BookingItemDAO.
        """
        return (
            Seat.query
            .filter_by(venue_id=venue_id, is_active=True)
            .all()
        )

    def update_seat(self, seat: Seat) -> Seat:
        """Commit any changes the Service already applied to `seat`."""
        try:
            db.session.commit()
            return seat
        except Exception:
            db.session.rollback()
            raise

    def delete_seat(self, seat: Seat) -> bool:
        """Delete the given seat row. Returns True on success."""
        try:
            db.session.delete(seat)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
