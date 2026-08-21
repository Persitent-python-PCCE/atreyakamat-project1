# Services/ticket_service.py
#
# Business logic for tickets and ticket verifications (the scan record).
#
# SCOPE for THIS phase:
#   - get a ticket by its unique token
#   - get a ticket by its booking
#   - record a verification attempt (the caller provides the status string;
#     no rule-based validation yet)
#   - update a ticket's status (status flip only)
#
# What this service does NOT do in this phase:
#   - decide the correct verification_status based on ticket state + event date
#   - flip the ticket to 'used' automatically on a 'valid' scan
#   - mark tickets expired at event date time
#   - reject scans of cancelled or rescheduled bookings  (booking linkage)
#   - keep a complete verification-history audit trail used in business logic
#
# All of these are deliberate deferrals to the later ticket-validity
# workflow and the booking cancellation workflow.

from DAO import TicketDAO, TicketVerificationDAO
from models.ticket_verification import TicketVerification
from api.serializers import ticket_to_dict, ticket_verification_to_dict
from Services._result import ok, fail


class TicketService:
    def __init__(self):
        self.ticket_dao = TicketDAO()
        self.verification_dao = TicketVerificationDAO()

    # ---------------- READ ticket ----------------
    def get_ticket_by_token(self, token: str) -> dict:
        if not token:
            return fail("Token is required", 400)
        t = self.ticket_dao.get_ticket_by_token(token)
        if t is None:
            return fail("Ticket not found", 404)
        return ok("Ticket retrieved", ticket_to_dict(t))

    def get_ticket_by_booking(self, booking_id: int) -> dict:
        t = self.ticket_dao.get_ticket_by_booking(booking_id)
        if t is None:
            return fail("Ticket not found for this booking", 404)
        return ok("Ticket retrieved", ticket_to_dict(t))

    def get_all_tickets(self) -> dict:
        tickets = self.ticket_dao.get_all_tickets()
        return ok("Tickets retrieved", [ticket_to_dict(t) for t in tickets])

    # ---------------- UPDATE ticket ----------------
    def update_ticket_status(self, ticket_id: int, data: dict) -> dict:
        """Flip a ticket's status. Expects {'ticket_status': 'used'|...}.
        """
        t = self.ticket_dao.get_ticket_by_id(ticket_id)
        if t is None:
            return fail("Ticket not found", 404)
        new_status = data.get("ticket_status")
        if not new_status:
            return fail("Missing required field: ticket_status", 400)
        t.ticket_status = new_status
        try:
            self.ticket_dao.update_ticket_status(t)
        except Exception:
            return fail("Could not update ticket status", 500)
        return ok("Ticket status updated", ticket_to_dict(t))

    # ---------------- VERIFY (record a scan) ----------------
    def verify_ticket(self, token: str, data: dict) -> dict:
        """Record a verification (scan) attempt for the ticket found by token.

        Required in `data`: verification_status
        (one of 'valid' / 'already_used' / 'expired' / 'invalid' in the design,
        but this basic phase accepts whatever the caller supplies.)
        """
        if not token:
            return fail("Token is required", 400)
        t = self.ticket_dao.get_ticket_by_token(token)
        if t is None:
            return fail("Ticket not found", 404)

        status = data.get("verification_status")
        if not status:
            return fail("Missing required field: verification_status", 400)

        verification = TicketVerification(
            ticket_id=t.id,
            verification_status=status,
        )
        try:
            saved = self.verification_dao.create_verification(verification)
        except Exception:
            return fail("Could not record verification", 500)
        return ok("Verification recorded",
                  ticket_verification_to_dict(saved), status=201)
