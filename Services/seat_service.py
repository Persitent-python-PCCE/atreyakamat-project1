# Services/seat_service.py
#
# Business logic for seats. A seat belongs to a Venue (per models/seat.py).
#
# This service does NOT implement the 1-minute seat-hold workflow — that is
# a SeatHold + Booking responsibility for a later phase. Here we only handle
# basic CRUD and the simple "active seats of a venue" lookup.

from DAO import SeatDAO, VenueDAO
from models.seat import Seat
from api.serializers import seat_to_dict
from Services._result import ok, fail


class SeatService:
    def __init__(self):
        self.seat_dao = SeatDAO()
        self.venue_dao = VenueDAO()  # used to validate venue existence

    # ---------------------------------------------------------------- #
    # CREATE (single)
    # ---------------------------------------------------------------- #
    def create_seat(self, data: dict) -> dict:
        """Create one seat.

        Required: venue_id, seat_number
        Optional: section_name, seat_type (default 'standard'),
                  price (default 0.00), is_active (default True)
        """
        venue_id = data.get("venue_id")
        seat_number = data.get("seat_number")

        if venue_id is None:
            return fail("Missing required field: venue_id", 400)
        if not seat_number or (isinstance(seat_number, str) and not seat_number.strip()):
            return fail("Missing required field: seat_number", 400)

        if self.venue_dao.get_venue_by_id(venue_id) is None:
            return fail("Venue not found", 404)

        seat = Seat(
            venue_id=venue_id,
            seat_number=seat_number,
            section_name=data.get("section_name"),
            seat_type=data.get("seat_type", "standard"),
            price=data.get("price", 0.00),
            is_active=bool(data.get("is_active", True)),
        )
        try:
            saved = self.seat_dao.create_seat(seat)
        except Exception:
            return fail("Could not create seat", 500)
        return ok("Seat created", seat_to_dict(saved), status=201)

    # ---------------------------------------------------------------- #
    # READ
    # ---------------------------------------------------------------- #
    def get_seat_by_id(self, seat_id: int) -> dict:
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None:
            return fail("Seat not found", 404)
        return ok("Seat retrieved", seat_to_dict(seat))

    def get_seats_by_venue(self, venue_id: int) -> dict:
        seats = self.seat_dao.get_seats_by_venue(venue_id)
        return ok("Seats retrieved", [seat_to_dict(s) for s in seats])

    def get_available_seats(self, venue_id: int) -> dict:
        """Basic available-seats list (active seats of a venue only).

        The full "minus held, minus sold" computation is deferred to the
        later booking workflow.
        """
        seats = self.seat_dao.get_available_seats(venue_id)
        return ok("Available seats retrieved", [seat_to_dict(s) for s in seats])

    # ---------------------------------------------------------------- #
    # UPDATE
    # ---------------------------------------------------------------- #
    def update_seat(self, seat_id: int, data: dict) -> dict:
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None:
            return fail("Seat not found", 404)

        for field in ["seat_number", "section_name", "seat_type", "price", "is_active"]:
            if field in data:
                setattr(seat, field, data[field])
        if "venue_id" in data:
            vid = data["venue_id"]
            if self.venue_dao.get_venue_by_id(vid) is None:
                return fail("Venue not found", 404)
            seat.venue_id = vid

        try:
            self.seat_dao.update_seat(seat)
        except Exception:
            return fail("Could not update seat", 500)
        return ok("Seat updated", seat_to_dict(seat))

    # ---------------------------------------------------------------- #
    # DELETE
    # ---------------------------------------------------------------- #
    def delete_seat(self, seat_id: int) -> dict:
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None:
            return fail("Seat not found", 404)
        try:
            self.seat_dao.delete_seat(seat)
        except Exception:
            return fail("Could not delete seat", 500)
        return ok("Seat deleted")
