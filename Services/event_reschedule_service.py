# Services/event_reschedule_service.py
#
# Business logic for event reschedules.
#
# SCOPE for THIS phase:
#   - create a reschedule record (audits old_date/old_time -> new_date/
#     new_time, reason, admin)
#   - read reschedule history by event / by admin
#   - delete a reschedule record (rare)
#
# What this service does NOT do in this phase:
#   - admin password confirmation (no auth here yet)
#   - actually mutating the Event row (event_date / status flip)
#   - notifying affected users
#   - sending reschedule emails
#
# Those belong to a later workflow that combines several services in one
# transaction. The methods below are written so that workflow can call
# them as building blocks.

from DAO import EventRescheduleDAO, EventDAO, UserDAO
from models.event_reschedule import EventReschedule
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


class EventRescheduleService:
    def __init__(self):
        self.reschedule_dao = EventRescheduleDAO()
        self.event_dao = EventDAO()
        self.user_dao = UserDAO()

    def create_reschedule(self, data: dict) -> dict:
        required = ("event_id", "admin_id", "old_event_date",
                    "old_start_time", "new_event_date", "new_start_time")
        for f in required:
            if data.get(f) in (None, ""):
                return fail(f"Missing required field: {f}", 400)

        # cross-checks
        if self.event_dao.get_event_by_id(data["event_id"]) is None:
            return fail("Event not found", 404)
        if self.user_dao.get_user_by_id(data["admin_id"]) is None:
            return fail("Admin user not found", 404)

        r = EventReschedule(
            event_id=data["event_id"],
            admin_id=data["admin_id"],
            old_event_date=data["old_event_date"],
            old_start_time=data["old_start_time"],
            new_event_date=data["new_event_date"],
            new_start_time=data["new_start_time"],
            reason=data.get("reason"),
        )
        try:
            saved = self.reschedule_dao.create_reschedule(r)
        except Exception:
            return fail("Could not create reschedule record", 500)
        return ok("Reschedule record created",
                  reschedule_to_dict(saved), status=201)

    def get_reschedule_by_id(self, reschedule_id: int) -> dict:
        r = self.reschedule_dao.get_reschedule_by_id(reschedule_id)
        if r is None:
            return fail("Reschedule record not found", 404)
        return ok("Reschedule record retrieved", reschedule_to_dict(r))

    def get_reschedules_by_event(self, event_id: int) -> dict:
        rows = self.reschedule_dao.get_reschedules_by_event(event_id)
        return ok("Event reschedule history retrieved",
                  [reschedule_to_dict(r) for r in rows])

    def get_reschedules_by_admin(self, admin_id: int) -> dict:
        rows = self.reschedule_dao.get_reschedules_by_admin(admin_id)
        return ok("Admin reschedule history retrieved",
                  [reschedule_to_dict(r) for r in rows])

    def delete_reschedule(self, reschedule_id: int) -> dict:
        r = self.reschedule_dao.get_reschedule_by_id(reschedule_id)
        if r is None:
            return fail("Reschedule record not found", 404)
        try:
            self.reschedule_dao.delete_reschedule(r)
        except Exception:
            return fail("Could not delete reschedule record", 500)
        return ok("Reschedule record deleted")
