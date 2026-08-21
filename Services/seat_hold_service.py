# Services/seat_hold_service.py
#
# Business logic for seat holds (the temporary lock placed on a seat
# during checkout).
#
# SCOPE for THIS phase (basic API):
#   - create a hold (the Service generates hold_token + expires_at if the
#     caller did not supply them)
#   - retrieve a hold by id / by token
#   - find the currently-active hold for an (event, seat) pair
#   - list all holds placed by a user
#   - list holds that are past their expires_at but still marked 'active'
#   - update a hold (status flip to 'expired' / 'released' / 'converted')
#   - delete a hold (permanent removal; rarely used)
#
# What this service does NOT do in this phase:
#   - the 1-minute expiry automation (no background job here)
#   - enforcing "only one active hold per (event, seat) at a time"
#     strictly — the basic API just records the row. A full booking
#     workflow will add this guard later (it requires coordinating with
#     BookingService in one DB transaction).

import uuid
from datetime import datetime, timedelta

from DAO import SeatHoldDAO, EventDAO, SeatDAO
from models.seat_hold import SeatHold
from api.serializers import _ser
from Services._result import ok, fail


def hold_to_dict(h):
    return {
        "id": h.id,
        "event_id": h.event_id,
        "seat_id": h.seat_id,
        "user_id": h.user_id,
        "hold_token": h.hold_token,
        "held_at": _ser(h.held_at),
        "expires_at": _ser(h.expires_at),
        "status": h.status,
    }


# The default hold duration if the caller did not supply an explicit
# expires_at. Expressed in seconds so it is easy to read & change.
DEFAULT_HOLD_SECONDS = 60


class SeatHoldService:
    def __init__(self):
        self.hold_dao = SeatHoldDAO()
        self.event_dao = EventDAO()
        self.seat_dao = SeatDAO()

    # ---------------- CREATE ----------------
    def create_hold(self, data: dict) -> dict:
        """Create a seat hold.

        Required: event_id, seat_id, user_id
        Optional: hold_token    (auto-generated if not provided),
                  expires_at     (defaults to now + DEFAULT_HOLD_SECONDS,
                                  but ignored if `expires_in_seconds` is
                                  supplied AND no `expires_at` is supplied),
                  expires_in_seconds (overrides default duration),
                  status          (default 'active')
        """
        for f in ("event_id", "seat_id", "user_id"):
            if data.get(f) is None:
                return fail(f"Missing required field: {f}", 400)

        # cross-checks
        if self.event_dao.get_event_by_id(data["event_id"]) is None:
            return fail("Event not found", 404)
        if self.seat_dao.get_seat_by_id(data["seat_id"]) is None:
            return fail("Seat not found", 404)
        # (We don't check the user here to keep the basic API simple; a
        # 404 user would just produce a parboiled FK violation caught below.)

        # Compute expires_at
        if "expires_at" in data and data["expires_at"] is not None:
            expires_at = data["expires_at"]
        else:
            secs = data.get("expires_in_seconds", DEFAULT_HOLD_SECONDS)
            expires_at = datetime.utcnow() + timedelta(seconds=secs)

        # Compute hold_token
        hold_token = data.get("hold_token") or f"HLD-{uuid.uuid4().hex[:16]}"

        hold = SeatHold(
            event_id=data["event_id"],
            seat_id=data["seat_id"],
            user_id=data["user_id"],
            hold_token=hold_token,
            expires_at=expires_at,
            status=data.get("status", "active"),
        )
        try:
            saved = self.hold_dao.create_hold(hold)
        except Exception:
            return fail("Could not create seat hold", 500)
        return ok("Seat hold created", hold_to_dict(saved), status=201)

    # ---------------- READ ----------------
    def get_hold_by_id(self, hold_id: int) -> dict:
        h = self.hold_dao.get_hold_by_id(hold_id)
        if h is None:
            return fail("Seat hold not found", 404)
        return ok("Seat hold retrieved", hold_to_dict(h))

    def get_hold_by_token(self, token: str) -> dict:
        h = self.hold_dao.get_hold_by_token(token)
        if h is None:
            return fail("Seat hold not found", 404)
        return ok("Seat hold retrieved", hold_to_dict(h))

    def get_active_hold(self, event_id: int, seat_id: int) -> dict:
        h = self.hold_dao.get_active_hold(event_id, seat_id)
        if h is None:
            return ok("No active hold on this seat", None)
        return ok("Active seat hold retrieved", hold_to_dict(h))

    def get_holds_by_user(self, user_id: int) -> dict:
        holds = self.hold_dao.get_holds_by_user(user_id)
        return ok("User seat holds retrieved", [hold_to_dict(h) for h in holds])

    def get_expired_holds(self) -> dict:
        """Return holds whose expires_at has passed but status is still
        'active'. The caller may flip them to 'expired' via update_hold.
        """
        holds = self.hold_dao.get_expired_holds()
        return ok("Expired (still-flagged-active) holds retrieved",
                  [hold_to_dict(h) for h in holds])

    # ---------------- UPDATE ----------------
    def update_hold(self, hold_id: int, data: dict) -> dict:
        h = self.hold_dao.get_hold_by_id(hold_id)
        if h is None:
            return fail("Seat hold not found", 404)

        # Only `status` is editable through this endpoint at this stage.
        if "status" in data:
            h.status = data["status"]
        if "expires_at" in data:
            h.expires_at = data["expires_at"]
        if "booking_id" in data:  # not a column for this model; ignored gracefully
            pass

        try:
            self.hold_dao.update_hold(h)
        except Exception:
            return fail("Could not update seat hold", 500)
        return ok("Seat hold updated", hold_to_dict(h))

    # ---------------- DELETE ----------------
    def delete_hold(self, hold_id: int) -> dict:
        h = self.hold_dao.get_hold_by_id(hold_id)
        if h is None:
            return fail("Seat hold not found", 404)
        try:
            self.hold_dao.delete_hold(h)
        except Exception:
            return fail("Could not delete seat hold", 500)
        return ok("Seat hold deleted")
