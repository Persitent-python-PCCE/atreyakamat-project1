# DAO/email_log_dao.py
#
# EmailLogDAO — Data Access Object for the `email_logs` table.
# Each row is an audit record for an outbound email (booking confirmation,
# ticket delivery, reschedule notice, password reset).
#
# The DAO does NOT send emails — that is a job for the Service / mail
# provider. The DAO only stores and retrieves these audit rows.

from app import db
from models.email_log import EmailLog


class EmailLogDAO:
    """Database operations for the EmailLog model."""

    def create_log(self, log: EmailLog) -> EmailLog:
        """Insert a new email log row.

        Typically created by the Service BEFORE attempting to send, with
        status="pending". The Service will later call update_log() to set
        status="sent" or status="failed".
        """
        try:
            db.session.add(log)
            db.session.commit()
            return log
        except Exception:
            db.session.rollback()
            raise

    def get_log_by_id(self, log_id: int) -> EmailLog | None:
        """Load one email log row by its primary key."""
        return db.session.get(EmailLog, log_id)

    def get_logs_by_user(self, user_id: int) -> list[EmailLog]:
        """Return every email log row that targets a given user."""
        return EmailLog.query.filter_by(user_id=user_id).all()

    def get_logs_by_booking(self, booking_id: int) -> list[EmailLog]:
        """Return every email log row linked to a given booking."""
        return EmailLog.query.filter_by(booking_id=booking_id).all()

    def get_logs_by_status(self, status: str) -> list[EmailLog]:
        """Return every email log row with a given status string,
        e.g. 'pending', 'sent', 'failed'."""
        return EmailLog.query.filter_by(status=status).all()

    def update_log(self, log: EmailLog) -> EmailLog:
        """Commit changes the Service already applied to `log`.

        Example: the Service sets log.status = "sent" and log.sent_at = now
        and then calls this method.
        """
        try:
            db.session.commit()
            return log
        except Exception:
            db.session.rollback()
            raise

    def delete_log(self, log: EmailLog) -> bool:
        """Delete the given email log row. Returns True on success."""
        try:
            db.session.delete(log)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
