# Services/venue_service.py
#
# Business logic for venues. Same pattern as the other simple services.

from DAO import VenueDAO
from models.venue import Venue
from api.serializers import venue_to_dict
from Services._result import ok, fail


class VenueService:
    def __init__(self):
        self.venue_dao = VenueDAO()

    # ---------------- CREATE ----------------
    def create_venue(self, data: dict) -> dict:
        """Create a venue. Required: name, address."""
        name = data.get("name")
        if not name or (isinstance(name, str) and not name.strip()):
            return fail("Missing required field: name", 400)
        address = data.get("address")
        if not address or (isinstance(address, str) and not address.strip()):
            return fail("Missing required field: address", 400)

        # basic sanity check: capacity must be a non-negative integer if given
        capacity = data.get("capacity", 0)
        if not isinstance(capacity, int) or capacity < 0:
            return fail("capacity must be a non-negative integer", 400)

        venue = Venue(
            name=name,
            address=address,
            city=data.get("city"),
            state=data.get("state"),
            capacity=capacity,
            venue_type=data.get("venue_type", "seated"),
        )
        try:
            saved = self.venue_dao.create_venue(venue)
        except Exception:
            return fail("Could not create venue", 500)
        return ok("Venue created", venue_to_dict(saved), status=201)

    # ---------------- READ ----------------
    def get_venue_by_id(self, venue_id: int) -> dict:
        venue = self.venue_dao.get_venue_by_id(venue_id)
        if venue is None:
            return fail("Venue not found", 404)
        return ok("Venue retrieved", venue_to_dict(venue))

    def get_all_venues(self) -> dict:
        venues = self.venue_dao.get_all_venues()
        return ok("Venues retrieved", [venue_to_dict(v) for v in venues])

    # ---------------- UPDATE ----------------
    def update_venue(self, venue_id: int, data: dict) -> dict:
        venue = self.venue_dao.get_venue_by_id(venue_id)
        if venue is None:
            return fail("Venue not found", 404)

        if "name" in data:
            venue.name = data["name"]
        if "address" in data:
            venue.address = data["address"]
        if "city" in data:
            venue.city = data["city"]
        if "state" in data:
            venue.state = data["state"]
        if "capacity" in data:
            c = data["capacity"]
            if not isinstance(c, int) or c < 0:
                return fail("capacity must be a non-negative integer", 400)
            venue.capacity = c
        if "venue_type" in data:
            venue.venue_type = data["venue_type"]

        try:
            self.venue_dao.update_venue(venue)
        except Exception:
            return fail("Could not update venue", 500)
        return ok("Venue updated", venue_to_dict(venue))

    # ---------------- DELETE ----------------
    def delete_venue(self, venue_id: int) -> dict:
        venue = self.venue_dao.get_venue_by_id(venue_id)
        if venue is None:
            return fail("Venue not found", 404)
        try:
            self.venue_dao.delete_venue(venue)
        except Exception:
            return fail("Could not delete venue", 500)
        return ok("Venue deleted")
