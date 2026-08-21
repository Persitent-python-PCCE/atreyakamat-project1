# Services/event_addon_service.py
#
# Business logic for event add-ons.

from DAO import EventAddonDAO, EventDAO
from models.event_addon import EventAddon
from api.serializers import _ser  # we have no specific addon serializer; build inline
from Services._result import ok, fail


def addon_to_dict(a):
    return {
        "id": a.id,
        "event_id": a.event_id,
        "name": a.name,
        "description": a.description,
        "price": _ser(a.price),
        "available_quantity": a.available_quantity,
        "is_active": a.is_active,
        "created_at": _ser(a.created_at),
    }


class EventAddonService:
    def __init__(self):
        self.addon_dao = EventAddonDAO()
        self.event_dao = EventDAO()

    def create_addon(self, data: dict) -> dict:
        name = data.get("name")
        event_id = data.get("event_id")
        if not name or (isinstance(name, str) and not name.strip()):
            return fail("Missing required field: name", 400)
        if event_id is None:
            return fail("Missing required field: event_id", 400)

        if self.event_dao.get_event_by_id(event_id) is None:
            return fail("Event not found", 404)

        addon = EventAddon(
            event_id=event_id,
            name=name,
            description=data.get("description"),
            price=data.get("price", 0.00),
            available_quantity=data.get("available_quantity", 0),
            is_active=bool(data.get("is_active", True)),
        )
        try:
            saved = self.addon_dao.create_addon(addon)
        except Exception:
            return fail("Could not create add-on", 500)
        return ok("Add-on created", addon_to_dict(saved), status=201)

    def get_addon_by_id(self, addon_id: int) -> dict:
        a = self.addon_dao.get_addon_by_id(addon_id)
        if a is None:
            return fail("Add-on not found", 404)
        return ok("Add-on retrieved", addon_to_dict(a))

    def get_addons_by_event(self, event_id: int) -> dict:
        addons = self.addon_dao.get_addons_by_event(event_id)
        return ok("Event add-ons retrieved", [addon_to_dict(a) for a in addons])

    def get_all_addons(self) -> dict:
        addons = self.addon_dao.get_all_addons()
        return ok("Add-ons retrieved", [addon_to_dict(a) for a in addons])

    def update_addon(self, addon_id: int, data: dict) -> dict:
        a = self.addon_dao.get_addon_by_id(addon_id)
        if a is None:
            return fail("Add-on not found", 404)

        for field in ["name", "description", "price",
                      "available_quantity", "is_active"]:
            if field in data:
                setattr(a, field, data[field])

        try:
            self.addon_dao.update_addon(a)
        except Exception:
            return fail("Could not update add-on", 500)
        return ok("Add-on updated", addon_to_dict(a))

    def delete_addon(self, addon_id: int) -> dict:
        a = self.addon_dao.get_addon_by_id(addon_id)
        if a is None:
            return fail("Add-on not found", 404)
        try:
            self.addon_dao.delete_addon(a)
        except Exception:
            return fail("Could not delete add-on", 500)
        return ok("Add-on deleted")
