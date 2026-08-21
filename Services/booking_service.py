# Services/booking_service.py
#
# Business logic for bookings.
#
# SCOPE for THIS phase:
#   - create a basic booking row (the Service generates booking_reference)
#   - retrieve a booking by id / by reference
#   - list a user's bookings
#   - update basic editable fields
#   - soft-cancel a booking (status -> 'cancelled'; booking row only)
#
# What this service does NOT do in this phase:
#   - seat-lock release on cancel
#   - totals calculation from booking items + add-ons
#   - promo code application
#   - cashback issuing
#   - automatic ticket creation
#   - email sending
#
# All of these require coordinated work across multiple DAOs and tables in
# one transaction. They belong in a later workflow expansion. The shape of
# the methods below is designed so the later workflow can wrap them.

import uuid

from DAO import BookingDAO, EventDAO, UserDAO
from models.booking import Booking
from api.serializers import booking_to_dict
from Services._result import ok, fail


def _make_booking_reference():
    """Generate a simple unique booking reference, e.g. SMU-7d3c9a2b1f04.

    Generation lives here (in the Service), not in the DAO. The DAO only
    persists what the Service gives it.
    """
    return "SMU-" + uuid.uuid4().hex[:12]


class BookingService:
    def __init__(self):
        self.booking_dao = BookingDAO()
        self.event_dao = EventDAO()
        self.user_dao = UserDAO()

    # ---------------- CREATE ----------------
    def create_booking(self, data: dict) -> dict:
        """Create a basic booking.

        Required: user_id, event_id
        Optional: total_amount, discount_amount, cashback_amount, status

        The Service always generates the booking_reference itself; the
        caller may NOT set it (if they try, it's ignored — see below).
        """
        user_id = data.get("user_id")
        event_id = data.get("event_id")
        if user_id is None:
            return fail("Missing required field: user_id", 400)
        if event_id is None:
            return fail("Missing required field: event_id", 400)

        if self.user_dao.get_user_by_id(user_id) is None:
            return fail("User not found", 404)
        if self.event_dao.get_event_by_id(event_id) is None:
            return fail("Event not found", 404)

        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            booking_reference=_make_booking_reference(),
            total_amount=data.get("total_amount", 0.00),
            discount_amount=data.get("discount_amount", 0.00),
            cashback_amount=data.get("cashback_amount", 0.00),
            status=data.get("status", "pending"),
        )
        try:
            saved = self.booking_dao.create_booking(booking)
        except Exception:
            return fail("Could not create booking", 500)
        return ok("Booking created", booking_to_dict(saved), status=201)

    # ---------------- READ ----------------
    def get_booking_by_id(self, booking_id: int) -> dict:
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)
        return ok("Booking retrieved", booking_to_dict(b))

    def get_booking_by_reference(self, reference: str) -> dict:
        if not reference:
            return fail("Reference is required", 400)
        b = self.booking_dao.get_booking_by_reference(reference)
        if b is None:
            return fail("Booking not found", 404)
        return ok("Booking retrieved", booking_to_dict(b))

    def get_user_bookings(self, user_id: int) -> dict:
        bookings = self.booking_dao.get_user_bookings(user_id)
        return ok("User bookings retrieved",
                  [booking_to_dict(b) for b in bookings])

    # ---------------- UPDATE ----------------
    def update_booking(self, booking_id: int, data: dict) -> dict:
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)

        for field in ["total_amount", "discount_amount",
                      "cashback_amount", "status"]:
            if field in data:
                setattr(b, field, data[field])

        try:
            self.booking_dao.update_booking(b)
        except Exception:
            return fail("Could not update booking", 500)
        return ok("Booking updated", booking_to_dict(b))

    # ---------------- CANCEL ----------------
    def cancel_booking(self, booking_id: int) -> dict:
        """Soft-cancel: status -> 'cancelled' on the booking row only.

        NOTE (basic phase): this does NOT release held seats, cancel
        tickets, refund cashback, or send a cancellation email. Those
        steps belong to the later booking workflow that runs in one
        transaction across multiple DAOs.
        """
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)

        # Allow cancelling from any non-terminal status. The full rule
        # ("can only cancel if currently pending/confirmed") belongs to
        # the later workflow.
        if b.status == "cancelled":
            return fail("Booking is already cancelled", 409)

        try:
            self.booking_dao.cancel_booking(b)
        except Exception:
            return fail("Could not cancel booking", 500)
        return ok("Booking cancelled", booking_to_dict(b))

    # ---------------- DELETE ----------------
    def delete_booking(self, booking_id: int) -> dict:
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)
        try:
            self.booking_dao.delete_booking(b)
        except Exception:
            return fail("Could not delete booking", 500)
        return ok("Booking deleted")
