# DAO/ticket_dao.py
#
# TicketDAO — Data Access Object for the `tickets` table.
# A ticket is the admission entitlement a customer gets after a confirmed
# booking. It carries a unique ticket_token (what the QR encodes).
#
# This DAO does NOT:
#   - generate QR images (Service later)
#   - mark a ticket 'used' automatically on verification (Service decides)
#   - expire tickets automatically (Service decides)

from app import db
from models.ticket import Ticket


class TicketDAO:
    """Database operations for the Ticket model."""

    def create_ticket(self, ticket: Ticket) -> Ticket:
        """Insert a new ticket row.

        The Service is expected to set booking_id, ticket_token, ticket_status,
        qr_data, issued_at. The DAO only persists it.
        """
        try:
            db.session.add(ticket)
            db.session.commit()
            return ticket
        except Exception:
            db.session.rollback()
            raise

    def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
        """Load one ticket by its primary key."""
        return db.session.get(Ticket, ticket_id)

    def get_ticket_by_token(self, ticket_token: str) -> Ticket | None:
        """Load one ticket by its unique token.

        This is the lookup used at the venue door: the scanner reads the token
        from the QR and the Service calls this method.
        """
        return Ticket.query.filter_by(ticket_token=ticket_token).first()

    def get_ticket_by_booking(self, booking_id: int) -> Ticket | None:
        """Load the (at most one) ticket for a given booking.

        The model defines booking_id as unique, so .first() gives the only
        match (or None).
        """
        return Ticket.query.filter_by(booking_id=booking_id).first()

    def get_all_tickets(self) -> list[Ticket]:
        """Return every ticket in the database."""
        return Ticket.query.all()

    def update_ticket_status(self, ticket: Ticket) -> Ticket:
        """Persist a status change the Service already applied to `ticket`.

        Example: the Service sets ticket.ticket_status = "used" or "expired"
        and then calls this method.
        """
        try:
            db.session.commit()
            return ticket
        except Exception:
            db.session.rollback()
            raise

    def delete_ticket(self, ticket: Ticket) -> bool:
        """Delete the given ticket row. Returns True on success."""
        try:
            db.session.delete(ticket)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
