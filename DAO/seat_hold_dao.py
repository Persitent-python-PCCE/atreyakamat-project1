# DAO/seat_hold_dao.py
#
# SeatHoldDAO — Data Access Object for the `seat_holds` table.
# A SeatHold is a temporary lock on a seat (e.g. the 1-minute checkout hold).
#
# IMPORTANT: This DAO does NOT implement the 1-minute expiry business rule.
# It only writes/reads rows. The Service will decide whether a hold is still
# valid by comparing expires_at to the current time.

from datetime import datetime

from app import db
from models.seat_hold import SeatHold


class SeatHoldDAO:
    """Database operations for the SeatHold model."""

    # ---------------- CREATE ----------------
    def create_hold(self, hold: SeatHold) -> SeatHold:
        """Insert a new seat hold row.

        The Service is expected to set:
          event_id, seat_id, user_id, hold_token, expires_at, status="active".
        """
        try:
            db.session.add(hold)
            db.session.commit()
            return hold
        except Exception:
            db.session.rollback()
            raise

    # ---------------- READ ----------------
    def get_hold_by_id(self, hold_id: int) -> SeatHold | None:
        """Load one hold by its primary key."""
        return db.session.get(SeatHold, hold_id)

    def get_hold_by_token(self, hold_token: str) -> SeatHold | None:
        """Load one hold by its unique token (useful for checkout lookup)."""
        return SeatHold.query.filter_by(hold_token=hold_token).first()

    def get_active_hold(self, event_id: int, seat_id: int) -> SeatHold | None:
        """Return the currently-active hold for a given (event, seat) pair.

        Returns None if there is no active hold on that seat.
        There should be at most one such hold — that rule is enforced by the
        Service, not by this DAO.
        """
        return (
            SeatHold.query
            .filter_by(event_id=event_id, seat_id=seat_id, status="active")
            .first()
        )

    def get_holds_by_user(self, user_id: int) -> list[SeatHold]:
        """Return all holds placed by a given user (any status)."""
        return SeatHold.query.filter_by(user_id=user_id).all()

    def get_expired_holds(self) -> list[SeatHold]:
        """Return holds whose expires_at is in the past AND are still 'active'.

        These are candidates for the Service to mark as 'expired' and free the
        seats. The actual status flip is done through update_hold().
        """
        now = datetime.utcnow()
        return (
            SeatHold.query
            .filter(SeatHold.status == "active", SeatHold.expires_at < now)
            .all()
        )

    # ---------------- UPDATE ----------------
    def update_hold(self, hold: SeatHold) -> SeatHold:
        """Commit changes the Service already applied to `hold`.

        Example: the Service sets hold.status = "expired" or "converted"
        and then calls this method to persist it.
        """
        try:
            db.session.commit()
            return hold
        except Exception:
            db.session.rollback()
            raise

    # ---------------- DELETE ----------------
    def delete_hold(self, hold: SeatHold) -> bool:
        """Permanently delete a hold row. Returns True on success.

        Most of the time the Service prefers to UPDATE the status to
        'released'/'expired' rather than deleting rows; but this method is
        available if a row truly needs to be removed.
        """
        try:
            db.session.delete(hold)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
