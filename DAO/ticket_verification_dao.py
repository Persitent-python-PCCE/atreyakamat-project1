# DAO/ticket_verification_dao.py
#
# TicketVerificationDAO — Data Access Object for the `ticket_verifications`
# table. Each row records one scan attempt at the venue door (success or
# failure), so history is auditable.

from app import db
from models.ticket_verification import TicketVerification


class TicketVerificationDAO:
    """Database operations for the TicketVerification model."""

    def create_verification(
        self, verification: TicketVerification
    ) -> TicketVerification:
        """Insert a new ticket verification row.

        The Service sets ticket_id, verification_status, verified_at.
        The DAO just persists it.
        """
        try:
            db.session.add(verification)
            db.session.commit()
            return verification
        except Exception:
            db.session.rollback()
            raise

    def get_verification_by_id(
        self, verification_id: int
    ) -> TicketVerification | None:
        """Load one verification record by its primary key."""
        return db.session.get(TicketVerification, verification_id)

    def get_verifications_by_ticket(self, ticket_id: int) -> list[TicketVerification]:
        """Return the full scan history of a ticket (ordered oldest first).

        Useful for the Service to decide if a ticket has already been scanned.
        """
        return (
            TicketVerification.query
            .filter_by(ticket_id=ticket_id)
            .order_by(TicketVerification.verified_at.asc())
            .all()
        )

    def update_verification(
        self, verification: TicketVerification
    ) -> TicketVerification:
        """Commit changes the Service already applied to `verification`."""
        try:
            db.session.commit()
            return verification
        except Exception:
            db.session.rollback()
            raise

    def delete_verification(self, verification: TicketVerification) -> bool:
        """Delete the given verification row. Returns True on success."""
        try:
            db.session.delete(verification)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
