# Services/event_reschedule_service.py
#
# Business logic for Event Rescheduling.
#
# Workflow:
#   1. Validates admin password.
#   2. Validates event existence, status, and new schedule dates.
#   3. Atomically updates Event schedule in database.
#   4. Creates EventReschedule audit record.
#   5. Reactivates any previously expired tickets.
#   6. Creates in-app Notification records for all affected customers.
#   7. Dispatches email notification (non-blocking).
#
# Architecture:
#   Controller -> EventRescheduleService -> DAO / MySQL

from datetime import datetime, date, time as dt_time
from werkzeug.security import check_password_hash

from app import db
from DAO import EventRescheduleDAO, EventDAO, UserDAO, BookingDAO, TicketDAO, NotificationDAO
from models.event_reschedule import EventReschedule
from models.notification import Notification
from api.serializers import _ser
from Services._result import ok, fail


def reschedule_to_dict(r):
    return {
        "id": r.id,
        "event_id": r.event_id,
        "admin_id": r.admin_id,
        "old_event_date": _ser(r.old_event_date),
        "old_start_time": _ser(r.old_start_time),
        "new_event_date": _ser(r.new_event_date),
        "new_start_time": _ser(r.new_start_time),
        "reason": r.reason,
        "rescheduled_at": _ser(r.rescheduled_at),
    }


def _parse_date(val):
    if isinstance(val, date):
        return val
    if isinstance(val, str) and val.strip():
        return datetime.strptime(val.strip(), "%Y-%m-%d").date()
    return None


def _parse_time(val):
    if isinstance(val, dt_time):
        return val
    if isinstance(val, str) and val.strip():
        t_str = val.strip()
        if len(t_str) == 5:
            return datetime.strptime(t_str, "%H:%M").time()
        elif len(t_str) == 8:
            return datetime.strptime(t_str, "%H:%M:%S").time()
    return None


class EventRescheduleService:
    def __init__(self):
        self.reschedule_dao = EventRescheduleDAO()
        self.event_dao = EventDAO()
        self.user_dao = UserDAO()
        self.booking_dao = BookingDAO()
        self.ticket_dao = TicketDAO()
        self.notification_dao = NotificationDAO()

    def reschedule_event(
        self,
        event_id: int,
        admin_id: int,
        password: str,
        new_event_date,
        new_start_time,
        new_end_time=None,
        reason: str | None = None,
    ) -> dict:
        """Execute atomic event rescheduling with admin password verification and user notifications."""
        # 1. Admin Verification & Password Confirmation
        admin = self.user_dao.get_user_by_id(admin_id)
        if not admin or admin.role != "admin":
            return fail("Admin user not found or unauthorized", 403)

        if not password or not check_password_hash(admin.password_hash, password):
            return fail("Incorrect admin password. Rescheduling cancelled.", 401)

        # 2. Event Validation
        event = self.event_dao.get_event_by_id(event_id)
        if not event:
            return fail("Event not found", 404)

        if event.status == "cancelled":
            return fail("Cannot reschedule a cancelled event.", 400)

        # 3. Parse & Validate New Schedule
        parsed_new_date = _parse_date(new_event_date)
        parsed_new_start_time = _parse_time(new_start_time)
        parsed_new_end_time = _parse_time(new_end_time) if new_end_time else None

        if not parsed_new_date:
            return fail("Valid new event date (YYYY-MM-DD) is required", 400)
        if not parsed_new_start_time:
            return fail("Valid new start time (HH:MM) is required", 400)

        today = date.today()
        if parsed_new_date < today:
            return fail(f"New event date ({parsed_new_date}) cannot be in the past.", 400)

        if parsed_new_date == event.event_date and parsed_new_start_time == event.start_time:
            return fail("New date and time are identical to the current schedule.", 400)

        # 4. Atomic Database Transaction
        old_date = event.event_date
        old_start_time = event.start_time
        old_date_str = str(old_date)
        old_time_str = str(old_start_time)
        new_date_str = str(parsed_new_date)
        new_time_str = str(parsed_new_start_time)

        try:
            # 4a. Update Event Model
            event.event_date = parsed_new_date
            event.start_time = parsed_new_start_time
            if parsed_new_end_time:
                event.end_time = parsed_new_end_time
            db.session.add(event)

            # 4b. Create EventReschedule Audit Row
            reschedule_row = EventReschedule(
                event_id=event.id,
                admin_id=admin.id,
                old_event_date=old_date,
                old_start_time=old_start_time,
                new_event_date=parsed_new_date,
                new_start_time=parsed_new_start_time,
                reason=reason.strip() if reason else None,
                rescheduled_at=datetime.utcnow(),
            )
            db.session.add(reschedule_row)

            # 4c. Load all confirmed bookings for this event
            confirmed_bookings = self.booking_dao.get_event_bookings(event.id)
            affected_bookings = [b for b in confirmed_bookings if b.status == "confirmed"]

            # Reactivate any tickets that were marked expired due to past date
            for b in affected_bookings:
                t = self.ticket_dao.get_ticket_by_booking(b.id)
                if t and t.ticket_status == "expired":
                    t.ticket_status = "valid"
                    t.expired_at = None
                    db.session.add(t)

            # 4d. Create in-app Notifications for affected customers
            notified_user_ids = set()
            for b in affected_bookings:
                if b.user_id not in notified_user_ids:
                    notif = Notification(
                        user_id=b.user_id,
                        title=f"Event Rescheduled: {event.title}",
                        message=(
                            f"Your event '{event.title}' has been rescheduled from {old_date_str} at {old_time_str} "
                            f"to {new_date_str} at {new_time_str}. Reason: {reason or 'Schedule updated by organizer'}. "
                            f"Your existing tickets and QR codes remain fully valid!"
                        ),
                        notification_type="event_reschedule",
                        is_read=False,
                        created_at=datetime.utcnow(),
                    )
                    db.session.add(notif)
                    notified_user_ids.add(b.user_id)

            # Commit the entire transaction
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return fail(f"Rescheduling transaction failed: {str(e)}", 500)

        # 5. Dispatch non-blocking email notifications
        try:
            from Services.email_service import EmailService
            email_svc = EmailService()
            for b in affected_bookings:
                email_svc.send_reschedule_email(
                    user_id=b.user_id,
                    booking_id=b.id,
                    event_title=event.title,
                    old_date_str=old_date_str,
                    old_time_str=old_time_str,
                    new_date_str=new_date_str,
                    new_time_str=new_time_str,
                    reason=reason,
                )
        except Exception:
            pass  # Non-blocking

        response_payload = {
            "reschedule_id": reschedule_row.id,
            "event_id": event.id,
            "event_title": event.title,
            "old_event_date": old_date_str,
            "old_start_time": old_time_str,
            "new_event_date": new_date_str,
            "new_start_time": new_time_str,
            "reason": reason,
            "affected_users_count": len(notified_user_ids),
            "rescheduled_at": reschedule_row.rescheduled_at.isoformat(),
        }

        return ok("Event rescheduled successfully", response_payload, status=200)

    def get_reschedule_history(self, event_id: int) -> dict:
        """Get chronological reschedule audit trail for an event."""
        rows = self.reschedule_dao.get_reschedules_by_event(event_id)
        history = []
        for r in rows:
            admin = self.user_dao.get_user_by_id(r.admin_id)
            history.append({
                "id": r.id,
                "event_id": r.event_id,
                "admin_name": admin.name if admin else "Admin",
                "old_event_date": _ser(r.old_event_date),
                "old_start_time": _ser(r.old_start_time),
                "new_event_date": _ser(r.new_event_date),
                "new_start_time": _ser(r.new_start_time),
                "reason": r.reason or "No reason provided",
                "rescheduled_at": _ser(r.rescheduled_at),
            })
        return ok("Reschedule history retrieved", history)

    def get_reschedules_by_event(self, event_id: int) -> dict:
        return self.get_reschedule_history(event_id)
