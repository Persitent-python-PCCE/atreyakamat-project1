# Services/event_service.py
#
# Business logic for events. This is the first service that does
# cross-model validation: creating or updating an event requires that
# the referenced category, venue, and creator (a User) actually exist.
#
# To do that, this service talks to CategoryDAO, VenueDAO and UserDAO
# directly (not to their services). This keeps the dependency graph flat
# and easy to follow: a Service is the place where multiple DAOs may be
# combined. Service -> Service calls can get tangled quickly, so we avoid
# them at this beginner stage.

from datetime import date, datetime

from DAO import EventDAO, CategoryDAO, VenueDAO, UserDAO
from models.event import Event
from api.serializers import event_to_dict
from Services._result import ok, fail


class EventService:
    def __init__(self):
        self.event_dao = EventDAO()
        # DAOs for related models we need to validate against.
        self.category_dao = CategoryDAO()
        self.venue_dao = VenueDAO()
        self.user_dao = UserDAO()

    # ---------------------------------------------------------------- #
    # CREATE
    # ---------------------------------------------------------------- #
    def create_event(self, data: dict) -> dict:
        """Create an event.

        Required fields: title, category_id, venue_id, created_by,
                         event_date, start_time
        Optional fields: description, end_time, poster, booking_open,
                         status, requires_seats, base_price
        """
        # 1) Required-field validation (presence + non-empty for strings)
        required_strings = ("title",)
        required_any = ("category_id", "venue_id", "created_by",
                        "event_date", "start_time")

        for field in required_strings:
            v = data.get(field)
            if v is None or (isinstance(v, str) and not v.strip()):
                return fail(f"Missing required field: {field}", 400)
        for field in required_any:
            if data.get(field) in (None, ""):
                return fail(f"Missing required field: {field}", 400)

        # 2) Cross-model existence checks.
        if self.category_dao.get_category_by_id(data["category_id"]) is None:
            return fail("Category not found", 404)
        if self.venue_dao.get_venue_by_id(data["venue_id"]) is None:
            return fail("Venue not found", 404)
        if self.user_dao.get_user_by_id(data["created_by"]) is None:
            return fail("Creator user not found", 404)

        # 3) Basic event_date sanity — must be a date object or a
        # YYYY-MM-DD string, and must not be in the past.
        ev_date = data["event_date"]
        if isinstance(ev_date, str):
            try:
                ev_date = date.fromisoformat(ev_date)
            except ValueError:
                return fail("event_date must be YYYY-MM-DD", 400)
        if not isinstance(ev_date, date) or isinstance(ev_date, datetime):
            return fail("event_date must be a date", 400)
        # Note: we do NOT reject past dates here because editing past draft
        # events is occasionally useful at this stage. The full rule
        # ("published events can't be in the past") belongs to a later
        # workflow and will be enforced there.

        # 4) Build the Event. We trust start_time/end_time come as time
        # objects or HH:MM:SS strings; Flask SQL will accept either.
        event = Event(
            title=data["title"],
            category_id=data["category_id"],
            venue_id=data["venue_id"],
            created_by=data["created_by"],
            description=data.get("description"),
            event_date=ev_date,
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            poster=data.get("poster"),
            booking_open=data.get("booking_open", True),
            status=data.get("status", "draft"),
            requires_seats=data.get("requires_seats", True),
            base_price=data.get("base_price", 0.00),
        )

        try:
            saved = self.event_dao.create_event(event)
        except Exception:
            return fail("Could not create event", 500)
        return ok("Event created", event_to_dict(saved), status=201)

    # ---------------------------------------------------------------- #
    # READ
    # ---------------------------------------------------------------- #
    def get_event_by_id(self, event_id: int) -> dict:
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)
        return ok("Event retrieved", event_to_dict(event))

    def get_all_events(self) -> dict:
        events = self.event_dao.get_all_events()
        return ok("Events retrieved", [event_to_dict(e) for e in events])

    def get_upcoming_events(self) -> dict:
        events = self.event_dao.get_upcoming_events()
        return ok("Upcoming events retrieved",
                  [event_to_dict(e) for e in events])

    def get_events_by_category(self, category_id: int) -> dict:
        # We don't fail if the category doesn't exist — the DAO will just
        # return an empty list, which is honest ("no events in that
        # category"). If the caller wants a clean 404, they can use the
        # Category API first.
        events = self.event_dao.get_events_by_category(category_id)
        return ok("Events by category retrieved",
                  [event_to_dict(e) for e in events])

    def search_events(self, search_term: str) -> dict:
        # Empty / missing search term -> empty list (not an error)
        events = self.event_dao.search_events(search_term or "")
        return ok("Search results retrieved",
                  [event_to_dict(e) for e in events])

    # ---------------------------------------------------------------- #
    # UPDATE
    # ---------------------------------------------------------------- #
    def update_event(self, event_id: int, data: dict) -> dict:
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)

        # If the caller is changing category_id / venue_id, the new ones
        # must still exist (same rule as create).
        if "category_id" in data:
            cid = data["category_id"]
            if self.category_dao.get_category_by_id(cid) is None:
                return fail("Category not found", 404)
            event.category_id = cid
        if "venue_id" in data:
            vid = data["venue_id"]
            if self.venue_dao.get_venue_by_id(vid) is None:
                return fail("Venue not found", 404)
            event.venue_id = vid

        # Plain editable fields
        for field in [
            "title", "description", "start_time", "end_time",
            "poster", "booking_open", "status", "requires_seats",
            "base_price",
        ]:
            if field in data:
                setattr(event, field, data[field])

        # event_date — parse/validate the same way as create
        if "event_date" in data:
            ev_date = data["event_date"]
            if isinstance(ev_date, str):
                try:
                    ev_date = date.fromisoformat(ev_date)
                except ValueError:
                    return fail("event_date must be YYYY-MM-DD", 400)
            if not isinstance(ev_date, date) or isinstance(ev_date, datetime):
                return fail("event_date must be a date", 400)
            event.event_date = ev_date

        try:
            self.event_dao.update_event(event)
        except Exception:
            return fail("Could not update event", 500)
        return ok("Event updated", event_to_dict(event))

    # ---------------------------------------------------------------- #
    # DELETE
    # ---------------------------------------------------------------- #
    def delete_event(self, event_id: int) -> dict:
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)
        try:
            self.event_dao.delete_event(event)
        except Exception:
            return fail("Could not delete event", 500)
        return ok("Event deleted")
