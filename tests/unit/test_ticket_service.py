# tests/unit/test_ticket_service.py
#
# Pure unit tests for TicketService and Ticket Verification logic.
# WHY: Validates critical physical entry rules:
#   1. Initial door scan must validate and mark ticket as 'used' with timestamp.
#   2. Anti-double scan protection: second scan attempt on already-used ticket is rejected with 409 Conflict.
#   3. Cancelled booking tickets are rejected at the door with 400.
#   4. Every scan attempt writes an audit log in TicketVerification.

import pytest
from datetime import datetime
from models.booking import Booking
from models.ticket import Ticket
from models.ticket_verification import TicketVerification
from Services.ticket_service import TicketService


@pytest.mark.unit
class TestTicketService:
    @pytest.fixture(autouse=True)
    def setup_service(self, db_session, customer_user, event):
        self.ticket_service = TicketService()
        self.db = db_session
        self.user = customer_user
        self.event = event

        self.booking = Booking(
            user_id=self.user.id,
            event_id=self.event.id,
            booking_reference="SMU-TESTSCAN-PYT",
            status="confirmed",
        )
        self.db.add(self.booking)
        self.db.commit()

    def test_verify_valid_ticket_first_scan_succeeds(self):
        """WHY: First scan at venue entrance succeeds, transitions status to 'used', and logs audit row."""
        ticket = Ticket(booking_id=self.booking.id, ticket_token="TKT-VALID-PYT-1", ticket_status="valid")
        self.db.add(ticket)
        self.db.commit()

        res = self.ticket_service.validate_and_verify_ticket("TKT-VALID-PYT-1", mark_as_used=True)
        assert res["success"] is True
        assert res["status"] == 200

        # Check DB
        self.db.expire_all()
        t_after = self.db.get(Ticket, ticket.id)
        assert t_after.ticket_status == "used"
        assert t_after.used_at is not None

        # Verify TicketVerification log
        verif = self.db.query(TicketVerification).filter_by(ticket_id=ticket.id).first()
        assert verif is not None
        assert verif.verification_status == "success"

    def test_verify_double_scan_rejected_with_409(self):
        """WHY: Anti-double scan protection prevents ticket reuse and fraud at venue gates (409 Conflict)."""
        initial_used_time = datetime(2026, 8, 20, 18, 0, 0)
        ticket = Ticket(
            booking_id=self.booking.id,
            ticket_token="TKT-USED-PYT-2",
            ticket_status="used",
            used_at=initial_used_time,
        )
        self.db.add(ticket)
        self.db.commit()

        res = self.ticket_service.validate_and_verify_ticket("TKT-USED-PYT-2", mark_as_used=True)
        assert res["success"] is False
        assert res["status"] == 409
        assert "already been used" in res["message"]

        # Ensure used_at was not overwritten
        self.db.expire_all()
        t_after = self.db.get(Ticket, ticket.id)
        assert t_after.used_at == initial_used_time

    def test_verify_cancelled_booking_ticket_rejected(self):
        """WHY: Ticket linked to a cancelled booking must be refused admission at the gate (400 Bad Request)."""
        self.booking.status = "cancelled"
        ticket = Ticket(booking_id=self.booking.id, ticket_token="TKT-CANC-PYT-3", ticket_status="valid")
        self.db.add_all([self.booking, ticket])
        self.db.commit()

        res = self.ticket_service.validate_and_verify_ticket("TKT-CANC-PYT-3", mark_as_used=True)
        assert res["success"] is False
        assert res["status"] == 400
        assert "cancelled" in res["message"].lower()

    def test_verify_nonexistent_ticket_returns_404(self):
        """WHY: Forged or non-existent ticket token returns 404."""
        res = self.ticket_service.validate_and_verify_ticket("TKT-DOES-NOT-EXIST")
        assert res["success"] is False
        assert res["status"] == 404
