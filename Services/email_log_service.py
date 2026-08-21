# Services/email_log_service.py
#
# Business logic for the email audit log.
#
# SCOPE for THIS phase: basic CRUD over EmailLog rows.
# No actual email sending happens here (and no email provider is wired up).
# A later workflow will create a "pending" log row, attempt to send, then
# flip status to "sent"/"failed" via update_log. The methods here remain
# unchanged regardless of which provider is later plugged in.

from DAO import EmailLogDAO
from models.email_log import EmailLog
from api.serializers import _ser
from Services._result import ok, fail


def email_log_to_dict(e):
    return {
        "id": e.id,
        "user_id": e.user_id,
        "booking_id": e.booking_id,
        "recipient_email": e.recipient_email,
        "subject": e.subject,
        "email_type": e.email_type,
        "status": e.status,
        "error_message": e.error_message,
        "sent_at": _ser(e.sent_at),
        "created_at": _ser(e.created_at),
    }


class EmailLogService:
    def __init__(self):
        self.log_dao = EmailLogDAO()

    def create_log(self, data: dict) -> dict:
        required = ("recipient_email", "subject", "email_type")
        for f in required:
            v = data.get(f)
            if v is None or (isinstance(v, str) and not v.strip()):
                return fail(f"Missing required field: {f}", 400)

        log = EmailLog(
            user_id=data.get("user_id"),
            booking_id=data.get("booking_id"),
            recipient_email=data["recipient_email"],
            subject=data["subject"],
            email_type=data["email_type"],
            status=data.get("status", "pending"),
            error_message=data.get("error_message"),
            sent_at=data.get("sent_at"),
        )
        try:
            saved = self.log_dao.create_log(log)
        except Exception:
            return fail("Could not create email log row", 500)
        return ok("Email log row created",
                  email_log_to_dict(saved), status=201)

    def get_log_by_id(self, log_id: int) -> dict:
        e = self.log_dao.get_log_by_id(log_id)
        if e is None:
            return fail("Email log not found", 404)
        return ok("Email log retrieved", email_log_to_dict(e))

    def get_logs_by_user(self, user_id: int) -> dict:
        rows = self.log_dao.get_logs_by_user(user_id)
        return ok("User email logs retrieved",
                  [email_log_to_dict(e) for e in rows])

    def get_logs_by_booking(self, booking_id: int) -> dict:
        rows = self.log_dao.get_logs_by_booking(booking_id)
        return ok("Booking email logs retrieved",
                  [email_log_to_dict(e) for e in rows])

    def get_logs_by_status(self, status: str) -> dict:
        if not status:
            return fail("status is required", 400)
        rows = self.log_dao.get_logs_by_status(status)
        return ok("Email logs by status retrieved",
                  [email_log_to_dict(e) for e in rows])

    def update_log(self, log_id: int, data: dict) -> dict:
        """Update an email log row. Typically used to flip status
        (pending -> sent / failed) after a send attempt.
        """
        e = self.log_dao.get_log_by_id(log_id)
        if e is None:
            return fail("Email log not found", 404)

        for field in ["status", "error_message", "sent_at"]:
            if field in data:
                setattr(e, field, data[field])

        try:
            self.log_dao.update_log(e)
        except Exception:
            return fail("Could not update email log", 500)
        return ok("Email log updated", email_log_to_dict(e))

    def delete_log(self, log_id: int) -> dict:
        e = self.log_dao.get_log_by_id(log_id)
        if e is None:
            return fail("Email log not found", 404)
        try:
            self.log_dao.delete_log(e)
        except Exception:
            return fail("Could not delete email log", 500)
        return ok("Email log deleted")
