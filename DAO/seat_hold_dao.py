# DAO/seat_hold_dao.py
#
# SeatHoldDAO — Data Access Object for the `seat_holds` table.
# A SeatHold is a temporary lock on a seat (e.g. the 1-minute checkout hold).

from datetime import datetime

from app import db
from models.seat_hold import SeatHold


class SeatHoldDAO:
    """Database operations for the SeatHold model."""

    # ---------------- CREATE ----------------
    def create_hold(self, hold: SeatHold) -> SeatHold:
        """Insert a new seat hold row."""
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
        """Load one hold by its unique token."""
        return SeatHold.query.filter_by(hold_token=hold_token).first()

    def get_active_hold(self, event_id: int, seat_id: int) -> SeatHold | None:
        """Return the active hold for a given (event, seat) pair."""
        return (
            SeatHold.query
            .filter_by(event_id=event_id, seat_id=seat_id, status="active")
            .first()
        )

    def get_active_holds_by_event(self, event_id: int) -> list[SeatHold]:
        """Return all active holds for an event."""
        now = datetime.utcnow()
        return (
            SeatHold.query
            .filter(
                SeatHold.event_id == event_id,
                SeatHold.status == "active",
                SeatHold.expires_at > now,
            )
            .all()
        )

    def get_active_holds_by_user(self, user_id: int, event_id: int | None = None) -> list[SeatHold]:
        """Return all active non-expired holds for a given user."""
        now = datetime.utcnow()
        query = SeatHold.query.filter(
            SeatHold.user_id == user_id,
            SeatHold.status == "active",
            SeatHold.expires_at > now,
        )
        if event_id:
            query = query.filter(SeatHold.event_id == event_id)
        return query.all()

    def get_holds_by_user(self, user_id: int) -> list[SeatHold]:
        """Return all holds placed by a given user (any status)."""
        return SeatHold.query.filter_by(user_id=user_id).all()

    def get_expired_holds(self) -> list[SeatHold]:
        """Return holds whose expires_at is in the past AND are still 'active'."""
        now = datetime.utcnow()
        return (
            SeatHold.query
            .filter(SeatHold.status == "active", SeatHold.expires_at <= now)
            .all()
        )

    # ---------------- UPDATE ----------------
    def update_hold(self, hold: SeatHold) -> SeatHold:
        """Commit changes applied to `hold`."""
        try:
            db.session.commit()
            return hold
        except Exception:
            db.session.rollback()
            raise

    # ---------------- DELETE ----------------
    def delete_hold(self, hold: SeatHold) -> bool:
        """Permanently delete a hold row."""
        try:
            db.session.delete(hold)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
