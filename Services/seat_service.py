# Services/seat_service.py
#
# Business logic for seats and the 1-minute Seat Hold system.
#
# Flow:
#   Controllers -> SeatService -> SeatDAO / SeatHoldDAO / EventDAO -> Models -> MySQL

from datetime import datetime, timedelta
import uuid

from DAO import SeatDAO, SeatHoldDAO, EventDAO, VenueDAO, UserDAO, BookingDAO
from models.seat import Seat
from models.seat_hold import SeatHold
from models.booking_item import BookingItem
from models.booking import Booking
from api.serializers import seat_to_dict, seat_hold_to_dict
from Services._result import ok, fail


class SeatService:
    def __init__(self):
        self.seat_dao = SeatDAO()
        self.seat_hold_dao = SeatHoldDAO()
        self.event_dao = EventDAO()
        self.venue_dao = VenueDAO()
        self.user_dao = UserDAO()
        self.booking_dao = BookingDAO()

    # ---------------------------------------------------------------- #
    # INTERNAL HELPERS
    # ---------------------------------------------------------------- #
    def _clean_expired_holds(self):
        """Mark all past-expiry active holds as 'expired'."""
        expired_holds = self.seat_hold_dao.get_expired_holds()
        for hold in expired_holds:
            hold.status = "expired"
            try:
                self.seat_hold_dao.update_hold(hold)
            except Exception:
                pass

    def _get_booked_seat_ids_for_event(self, event_id: int) -> set[int]:
        """Return a set of seat IDs that are booked for this event."""
        # Find booking items attached to non-cancelled bookings for this event
        booked_items = (
            BookingItem.query
            .join(Booking, BookingItem.booking_id == Booking.id)
            .filter(
                Booking.event_id == event_id,
                Booking.status.in_(["confirmed", "completed", "pending"]),
                BookingItem.seat_id.isnot(None),
            )
            .all()
        )
        return {item.seat_id for item in booked_items if item.seat_id is not None}

    # ---------------------------------------------------------------- #
    # SEAT MAP FOR EVENT
    # ---------------------------------------------------------------- #
    def get_event_seat_map(self, event_id: int, user_id: int | None = None) -> dict:
        """Return the visual seat map for an event with availability & hold states."""
        # 1. Validate event
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)

        # 2. Expire old holds
        self._clean_expired_holds()

        # 3. Load all seats for event's venue
        all_seats = self.seat_dao.get_seats_by_venue(event.venue_id)

        # 4. Load booked seats
        booked_seat_ids = self._get_booked_seat_ids_for_event(event_id)

        # 5. Load active holds for this event
        now = datetime.utcnow()
        active_holds = self.seat_hold_dao.get_active_holds_by_event(event_id)
        hold_by_seat_id = {h.seat_id: h for h in active_holds}

        # 6. Build enriched seat list
        seat_data_list = []
        user_held_count = 0
        user_total_price = 0.0

        for seat in all_seats:
            if not seat.is_active:
                continue

            seat_price = float(seat.price if seat.price and seat.price > 0 else (event.base_price or 0.0))
            hold = hold_by_seat_id.get(seat.id)

            if seat.id in booked_seat_ids:
                status = "booked"
                is_available = False
                hold_info = None
            elif hold:
                if user_id and hold.user_id == user_id:
                    status = "held_by_me"
                    is_available = True
                    remaining = max(0, int((hold.expires_at - now).total_seconds()))
                    hold_info = {
                        "hold_token": hold.hold_token,
                        "expires_at": hold.expires_at.isoformat(),
                        "remaining_seconds": remaining,
                    }
                    user_held_count += 1
                    user_total_price += seat_price
                else:
                    status = "held"
                    is_available = False
                    hold_info = None
            else:
                status = "available"
                is_available = True
                hold_info = None

            seat_dict = {
                "id": seat.id,
                "seat_number": seat.seat_number,
                "section_name": seat.section_name or "General",
                "seat_type": seat.seat_type,
                "price": seat_price,
                "status": status,
                "is_available": is_available,
                "hold": hold_info,
            }
            seat_data_list.append(seat_dict)

        summary = {
            "total_seats": len(seat_data_list),
            "available_seats": sum(1 for s in seat_data_list if s["status"] == "available"),
            "booked_seats": len(booked_seat_ids),
            "held_seats": len(active_holds),
            "user_held_count": user_held_count,
            "user_total_price": round(user_total_price, 2),
        }

        return ok("Seat map retrieved", {"seats": seat_data_list, "summary": summary})

    # ---------------------------------------------------------------- #
    # 1-MINUTE SEAT HOLD
    # ---------------------------------------------------------------- #
    def hold_seat(self, event_id: int, seat_id: int, user_id: int) -> dict:
        """Place a 1-minute temporary hold on a seat for a user."""
        # 1. Expire outdated holds
        self._clean_expired_holds()

        # 2. Validate Event
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)

        # 3. Validate Seat
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None or seat.venue_id != event.venue_id or not seat.is_active:
            return fail("Seat not found for this venue", 404)

        # 4. Check if seat is already booked
        booked_ids = self._get_booked_seat_ids_for_event(event_id)
        if seat_id in booked_ids:
            return fail("This seat is already booked", 409)

        # 5. Check if active hold exists
        now = datetime.utcnow()
        active_hold = self.seat_hold_dao.get_active_hold(event_id, seat_id)
        if active_hold:
            if active_hold.expires_at > now:
                if active_hold.user_id == user_id:
                    # Already held by this user — return existing hold
                    rem = max(0, int((active_hold.expires_at - now).total_seconds()))
                    return ok(
                        "Seat is already held by you",
                        {
                            "hold_token": active_hold.hold_token,
                            "seat_id": seat_id,
                            "event_id": event_id,
                            "expires_at": active_hold.expires_at.isoformat(),
                            "remaining_seconds": rem,
                        },
                        status=200,
                    )
                else:
                    # Held by someone else
                    return fail("Seat is currently held by another user", 409)
            else:
                # Hold has expired
                active_hold.status = "expired"
                self.seat_hold_dao.update_hold(active_hold)

        # 6. Create 1-minute SeatHold
        token = str(uuid.uuid4())
        held_at = datetime.utcnow()
        expires_at = held_at + timedelta(minutes=1)

        new_hold = SeatHold(
            event_id=event_id,
            seat_id=seat_id,
            user_id=user_id,
            hold_token=token,
            held_at=held_at,
            expires_at=expires_at,
            status="active",
        )

        try:
            saved_hold = self.seat_hold_dao.create_hold(new_hold)
        except Exception:
            return fail("Could not create seat hold", 500)

        rem_seconds = max(0, int((saved_hold.expires_at - datetime.utcnow()).total_seconds()))

        return ok(
            "Seat held successfully for 1 minute",
            {
                "hold_token": saved_hold.hold_token,
                "seat_id": seat_id,
                "event_id": event_id,
                "expires_at": saved_hold.expires_at.isoformat(),
                "remaining_seconds": rem_seconds,
            },
            status=201,
        )

    # ---------------------------------------------------------------- #
    # RELEASE SEAT HOLD
    # ---------------------------------------------------------------- #
    def release_seat_hold(self, event_id: int, seat_id: int, user_id: int) -> dict:
        """Release a user's active hold on a seat."""
        active_hold = self.seat_hold_dao.get_active_hold(event_id, seat_id)
        if active_hold is None or active_hold.user_id != user_id or active_hold.status != "active":
            return fail("Active hold not found for this user", 404)

        active_hold.status = "released"
        try:
            self.seat_hold_dao.update_hold(active_hold)
        except Exception:
            return fail("Could not release hold", 500)

        return ok("Seat hold released successfully")

    def release_by_token(self, hold_token: str, user_id: int) -> dict:
        """Release a hold by its unique token."""
        hold = self.seat_hold_dao.get_hold_by_token(hold_token)
        if hold is None or hold.user_id != user_id:
            return fail("Hold not found", 404)

        hold.status = "released"
        try:
            self.seat_hold_dao.update_hold(hold)
        except Exception:
            return fail("Could not release hold", 500)

        return ok("Seat hold released successfully")

    def get_user_active_holds(self, user_id: int, event_id: int | None = None) -> dict:
        """Return all active, non-expired holds for a user."""
        self._clean_expired_holds()
        holds = self.seat_hold_dao.get_active_holds_by_user(user_id, event_id)
        now = datetime.utcnow()
        result_data = []
        for h in holds:
            rem = max(0, int((h.expires_at - now).total_seconds()))
            item = seat_hold_to_dict(h)
            item["remaining_seconds"] = rem
            result_data.append(item)
        return ok("User active holds retrieved", result_data)

    # ---------------------------------------------------------------- #
    # BASIC SEAT CRUD
    # ---------------------------------------------------------------- #
    def create_seat(self, data: dict) -> dict:
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

    def get_seat_by_id(self, seat_id: int) -> dict:
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None:
            return fail("Seat not found", 404)
        return ok("Seat retrieved", seat_to_dict(seat))

    def get_seats_by_venue(self, venue_id: int) -> dict:
        seats = self.seat_dao.get_seats_by_venue(venue_id)
        return ok("Seats retrieved", [seat_to_dict(s) for s in seats])

    def get_available_seats(self, venue_id: int) -> dict:
        seats = self.seat_dao.get_available_seats(venue_id)
        return ok("Available seats retrieved", [seat_to_dict(s) for s in seats])

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

    def delete_seat(self, seat_id: int) -> dict:
        seat = self.seat_dao.get_seat_by_id(seat_id)
        if seat is None:
            return fail("Seat not found", 404)
        try:
            self.seat_dao.delete_seat(seat)
        except Exception:
            return fail("Could not delete seat", 500)
        return ok("Seat deleted")

    def generate_seats_grid(
        self,
        venue_id: int,
        num_rows: int = 5,
        seats_per_row: int = 10,
        section_name: str = "Orchestra",
        seat_type: str = "standard",
        price: float = 0.00,
    ) -> dict:
        """Generate a grid of seats (e.g. Rows A-E, 1-10) for a venue."""
        venue = self.venue_dao.get_venue_by_id(venue_id)
        if venue is None:
            return fail("Venue not found", 404)

        if num_rows < 1 or num_rows > 26:
            return fail("Number of rows must be between 1 and 26", 400)
        if seats_per_row < 1 or seats_per_row > 100:
            return fail("Seats per row must be between 1 and 100", 400)

        existing_seats = self.seat_dao.get_seats_by_venue(venue_id)
        existing_numbers = {s.seat_number for s in existing_seats}

        import string
        row_letters = string.ascii_uppercase[:num_rows]

        new_seats = []
        for row in row_letters:
            for num in range(1, seats_per_row + 1):
                seat_num = f"{row}-{num}"
                if seat_num not in existing_numbers:
                    new_seats.append(
                        Seat(
                            venue_id=venue_id,
                            seat_number=seat_num,
                            section_name=section_name or "General",
                            seat_type=seat_type or "standard",
                            price=float(price or 0.0),
                            is_active=True,
                        )
                    )

        if not new_seats:
            return ok("No new seats needed to be generated (all already exist)", {"created_count": 0})

        try:
            from app import db
            db.session.add_all(new_seats)
            db.session.commit()
        except Exception:
            return fail("Could not generate seats in database", 500)

        return ok(f"Successfully generated {len(new_seats)} seats for {venue.name}", {"created_count": len(new_seats)}, status=201)

    def clear_venue_seats(self, venue_id: int) -> dict:
        """Clear all seats for a venue."""
        venue = self.venue_dao.get_venue_by_id(venue_id)
        if venue is None:
            return fail("Venue not found", 404)

        existing_seats = self.seat_dao.get_seats_by_venue(venue_id)
        if not existing_seats:
            return ok("Venue already has no seats")

        try:
            from app import db
            for seat in existing_seats:
                db.session.delete(seat)
            db.session.commit()
        except Exception:
            return fail("Could not clear venue seats. Some seats may be referenced by active bookings.", 400)

        return ok("All seats for this venue have been cleared.")
