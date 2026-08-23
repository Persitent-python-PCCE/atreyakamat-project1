# Services/ticket_service.py
#
# Business logic for Tickets and QR Code Verification.
#
# Flow:
#   Controllers -> TicketService -> TicketDAO / TicketVerificationDAO / BookingDAO -> MySQL

from datetime import datetime, date
import uuid

from DAO import (
    TicketDAO,
    TicketVerificationDAO,
    BookingDAO,
    EventDAO,
    VenueDAO,
    SeatDAO,
    UserDAO,
    BookingItemDAO,
    BookingAddonDAO,
    EventAddonDAO,
)
from models.ticket import Ticket
from models.ticket_verification import TicketVerification
from api.serializers import ticket_to_dict, ticket_verification_to_dict
from Services._result import ok, fail


def _make_ticket_token():
    """Generate a cryptographically/randomly unique ticket token, e.g. TKT-3F8B2C9A1E04."""
    return "TKT-" + uuid.uuid4().hex[:16].upper()


class TicketService:
    def __init__(self):
        self.ticket_dao = TicketDAO()
        self.verification_dao = TicketVerificationDAO()
        self.booking_dao = BookingDAO()
        self.event_dao = EventDAO()
        self.venue_dao = VenueDAO()
        self.seat_dao = SeatDAO()
        self.user_dao = UserDAO()
        self.booking_item_dao = BookingItemDAO()
        self.booking_addon_dao = BookingAddonDAO()
        self.event_addon_dao = EventAddonDAO()

    # ---------------- CREATE TICKET ----------------
    def create_ticket_for_booking(self, booking_id: int) -> dict:
        """Create a single unique ticket for a confirmed booking (prevents duplicates)."""
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if booking is None:
            return fail("Booking not found", 404)

        if booking.status != "confirmed":
            return fail(f"Cannot generate ticket for non-confirmed booking (status: {booking.status})", 400)

        # Duplicate Prevention: Check if ticket already exists
        existing_ticket = self.ticket_dao.get_ticket_by_booking(booking_id)
        if existing_ticket is not None:
            return ok("Ticket already exists for this booking", ticket_to_dict(existing_ticket), status=200)

        token = _make_ticket_token()
        # QR data represents the verification token/URL — no sensitive customer data encoded directly
        qr_data = f"/verify/{token}"

        ticket = Ticket(
            booking_id=booking.id,
            ticket_token=token,
            ticket_status="valid",
            qr_data=qr_data,
            issued_at=datetime.utcnow(),
        )

        try:
            saved_ticket = self.ticket_dao.create_ticket(ticket)
        except Exception as e:
            return fail(f"Could not create ticket: {str(e)}", 500)

        return ok("Ticket created successfully", ticket_to_dict(saved_ticket), status=201)

    # ---------------- READ TICKET DETAILS ----------------
    def get_ticket_details_by_token(self, token: str) -> dict:
        """Retrieve full rich ticket details for customer view or verification."""
        if not token or not token.strip():
            return fail("Ticket token is required", 400)

        cleaned_token = token.strip()
        ticket = self.ticket_dao.get_ticket_by_token(cleaned_token)
        if ticket is None:
            return fail("Ticket not found", 404)

        booking = self.booking_dao.get_booking_by_id(ticket.booking_id)
        if booking is None:
            return fail("Associated booking not found", 404)

        user = self.user_dao.get_user_by_id(booking.user_id)
        event = self.event_dao.get_event_by_id(booking.event_id)
        venue = self.venue_dao.get_venue_by_id(event.venue_id) if event else None

        # Seats
        items = self.booking_item_dao.get_items_by_booking(booking.id)
        seat_numbers = []
        for it in items:
            if it.seat_id:
                s = self.seat_dao.get_seat_by_id(it.seat_id)
                if s:
                    seat_numbers.append(s.seat_number)

        # Add-ons
        b_addons = self.booking_addon_dao.get_addons_by_booking(booking.id)
        addons_list = []
        for ba in b_addons:
            ad = self.event_addon_dao.get_addon_by_id(ba.addon_id)
            addons_list.append({
                "name": ad.name if ad else "Add-on",
                "quantity": ba.quantity,
            })

        data = {
            "ticket_id": ticket.id,
            "ticket_token": ticket.ticket_token,
            "ticket_status": ticket.ticket_status,
            "qr_data": ticket.qr_data,
            "issued_at": ticket.issued_at.isoformat() if ticket.issued_at else None,
            "used_at": ticket.used_at.isoformat() if ticket.used_at else None,
            "expired_at": ticket.expired_at.isoformat() if ticket.expired_at else None,
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "total_amount": float(booking.total_amount),
            "customer_name": user.name if user else "Customer",
            "customer_email": user.email if user else "",
            "event_id": event.id if event else None,
            "event_title": event.title if event else "Event",
            "event_date": str(event.event_date) if event else "",
            "start_time": str(event.start_time) if event else "",
            "end_time": str(event.end_time) if event and event.end_time else None,
            "venue_name": venue.name if venue else "Main Venue",
            "venue_address": venue.address if venue else "",
            "venue_city": venue.city if venue else "",
            "seats": seat_numbers,
            "addons": addons_list,
        }

        return ok("Ticket details retrieved", data)

    def get_ticket_by_booking(self, booking_id: int) -> dict:
        """Get ticket by booking ID."""
        ticket = self.ticket_dao.get_ticket_by_booking(booking_id)
        if ticket is None:
            return fail("Ticket not found for this booking", 404)
        return self.get_ticket_details_by_token(ticket.ticket_token)

    # ---------------- VERIFY TICKET (SCAN AT VENUE DOOR) ----------------
    def validate_and_verify_ticket(self, token: str, mark_as_used: bool = True) -> dict:
        """Validate a ticket token against database rules and record the verification scan."""
        if not token or not token.strip():
            return fail("Ticket token is required", 400)

        cleaned_token = token.strip()
        ticket = self.ticket_dao.get_ticket_by_token(cleaned_token)

        # 1. Check: Ticket exists
        if ticket is None:
            return fail("Invalid ticket token: Ticket not found in system.", 404)

        # 2. Check: Associated Booking exists and is valid
        booking = self.booking_dao.get_booking_by_id(ticket.booking_id)
        if booking is None or booking.status == "cancelled":
            # Record failed verification
            verification = TicketVerification(
                ticket_id=ticket.id,
                verification_status="cancelled_booking",
                verified_at=datetime.utcnow(),
            )
            self.verification_dao.create_verification(verification)
            ticket.ticket_status = "cancelled"
            self.ticket_dao.update_ticket_status(ticket)
            return fail("Ticket verification failed: The associated booking has been cancelled.", 400)

        # 3. Check: Associated Event exists
        event = self.event_dao.get_event_by_id(booking.event_id)
        if event is None:
            verification = TicketVerification(
                ticket_id=ticket.id,
                verification_status="event_not_found",
                verified_at=datetime.utcnow(),
            )
            self.verification_dao.create_verification(verification)
            return fail("Ticket verification failed: Event not found.", 404)

        # 4. Check: Event date has not passed
        today = date.today()
        if event.event_date < today:
            ticket.ticket_status = "expired"
            ticket.expired_at = datetime.utcnow()
            self.ticket_dao.update_ticket_status(ticket)

            verification = TicketVerification(
                ticket_id=ticket.id,
                verification_status="expired_event",
                verified_at=datetime.utcnow(),
            )
            self.verification_dao.create_verification(verification)
            return fail(
                f"Ticket verification failed: The event date ({event.event_date}) has already passed.",
                400,
            )

        # 5. Check: Ticket has not already been used or invalidated
        if ticket.ticket_status == "used":
            verification = TicketVerification(
                ticket_id=ticket.id,
                verification_status="already_used",
                verified_at=datetime.utcnow(),
            )
            self.verification_dao.create_verification(verification)
            used_time_str = str(ticket.used_at) if ticket.used_at else "earlier"
            return fail(
                f"Ticket verification failed: This ticket has already been used for entry at {used_time_str}.",
                409,
            )

        if ticket.ticket_status in ["expired", "cancelled"]:
            verification = TicketVerification(
                ticket_id=ticket.id,
                verification_status=ticket.ticket_status,
                verified_at=datetime.utcnow(),
            )
            self.verification_dao.create_verification(verification)
            return fail(f"Ticket verification failed: Ticket status is {ticket.ticket_status}.", 400)

        # 6. Ticket is VALID! Mark as used if requested
        if mark_as_used:
            ticket.ticket_status = "used"
            ticket.used_at = datetime.utcnow()
            self.ticket_dao.update_ticket_status(ticket)

        # Record successful verification attempt
        verification = TicketVerification(
            ticket_id=ticket.id,
            verification_status="valid",
            verified_at=datetime.utcnow(),
        )
        self.verification_dao.create_verification(verification)

        # Load rich details for response
        user = self.user_dao.get_user_by_id(booking.user_id)
        venue = self.venue_dao.get_venue_by_id(event.venue_id)
        items = self.booking_item_dao.get_items_by_booking(booking.id)
        seats = [
            self.seat_dao.get_seat_by_id(it.seat_id).seat_number
            for it in items
            if it.seat_id and self.seat_dao.get_seat_by_id(it.seat_id)
        ]

        verification_payload = {
            "ticket_token": ticket.ticket_token,
            "verification_status": "valid",
            "verified_at": verification.verified_at.isoformat(),
            "ticket_status": ticket.ticket_status,
            "booking_reference": booking.booking_reference,
            "customer_name": user.name if user else "Customer",
            "event_title": event.title,
            "event_date": str(event.event_date),
            "start_time": str(event.start_time),
            "venue_name": venue.name if venue else "Main Venue",
            "seats": seats,
        }

        return ok("Ticket verified successfully! Admission granted.", verification_payload, status=200)

    def get_ticket_verifications(self, ticket_id: int) -> dict:
        """Get scan history audit trail for a ticket."""
        verifications = self.verification_dao.get_verifications_by_ticket(ticket_id)
        return ok(
            "Ticket verifications retrieved",
            [ticket_verification_to_dict(v) for v in verifications],
        )
