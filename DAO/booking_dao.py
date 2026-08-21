# DAO/booking_dao.py
#
# BookingDAO — Data Access Object for the `bookings` table.
# A booking is the central order a customer places for an event.
#
# This DAO does NOT calculate totals, apply promo codes, issue cashback,
# create tickets, or release seats. Those are Service-layer concerns.
# It only writes/reads booking rows.

from app import db
from models.booking import Booking


class BookingDAO:
    """Database operations for the Booking model."""

    # ---------------- CREATE ----------------
    def create_booking(self, booking: Booking) -> Booking:
        """Insert a new booking row.

        The Service is expected to set:
          user_id, event_id, booking_reference, total_amount, status, etc.
        """
        try:
            db.session.add(booking)
            db.session.commit()
            return booking
        except Exception:
            db.session.rollback()
            raise

    # ---------------- READ ----------------
    def get_booking_by_id(self, booking_id: int) -> Booking | None:
        """Load one booking by its primary key."""
        return db.session.get(Booking, booking_id)

    def get_booking_by_reference(self, reference: str) -> Booking | None:
        """Load one booking by its human-friendly booking_reference.

        booking_reference is unique on the model, so .first() gives the only
        match (or None).
        """
        return Booking.query.filter_by(booking_reference=reference).first()

    def get_user_bookings(self, user_id: int) -> list[Booking]:
        """Return all bookings placed by a given user (any status)."""
        return Booking.query.filter_by(user_id=user_id).all()

    def get_event_bookings(self, event_id: int) -> list[Booking]:
        """Return all bookings for a given event (any status)."""
        return Booking.query.filter_by(event_id=event_id).all()

    def get_all_bookings(self) -> list[Booking]:
        """Return every booking in the database."""
        return Booking.query.all()

    # ---------------- UPDATE ----------------
    def update_booking(self, booking: Booking) -> Booking:
        """Commit changes the Service already applied to `booking`.

        Example: the Service sets booking.status = "confirmed" and then
        calls this method to persist it.
        """
        try:
            db.session.commit()
            return booking
        except Exception:
            db.session.rollback()
            raise

    def cancel_booking(self, booking: Booking) -> Booking:
        """Mark a booking as cancelled by setting status='cancelled'.

        This is a thin wrapper — the Service is responsible for also
        releasing seats, cancelling tickets, etc. The DAO only persists
        the status change on the booking row itself.
        """
        # We set a field here because 'cancel' is a clear, single-purpose
        # operation tied to one column. If you prefer the Service to be the
        # ONLY place that sets fields, you can replace this method body with
        # just an update_booking(booking) call.
        booking.status = "cancelled"
        try:
            db.session.commit()
            return booking
        except Exception:
            db.session.rollback()
            raise

    # ---------------- DELETE ----------------
    def delete_booking(self, booking: Booking) -> bool:
        """Permanently delete a booking row. Returns True on success.

        This is rarely used in production (we normally cancel, not delete).
        Provided here for completeness and admin/test convenience.
        """
        try:
            db.session.delete(booking)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
