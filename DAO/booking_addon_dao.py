# DAO/booking_addon_dao.py
#
# BookingAddonDAO — Data Access Object for the `booking_addons` table.
# A BookingAddon is one add-on line chosen during checkout (ties a Booking
# to an EventAddon with the price snapshotted at purchase time).

from app import db
from models.booking_addon import BookingAddon


class BookingAddonDAO:
    """Database operations for the BookingAddon model."""

    def create_addon(self, addon: BookingAddon) -> BookingAddon:
        """Insert one new booking add-on row."""
        try:
            db.session.add(addon)
            db.session.commit()
            return addon
        except Exception:
            db.session.rollback()
            raise

    def create_addons_bulk(self, addons: list[BookingAddon]) -> list[BookingAddon]:
        """Insert many booking add-ons in one transaction (all-or-nothing)."""
        try:
            for a in addons:
                db.session.add(a)
            db.session.commit()
            return addons
        except Exception:
            db.session.rollback()
            raise

    def get_addon_by_id(self, addon_id: int) -> BookingAddon | None:
        """Load one booking add-on by its primary key."""
        return db.session.get(BookingAddon, addon_id)

    def get_addons_by_booking(self, booking_id: int) -> list[BookingAddon]:
        """Return every add-on line for a given booking."""
        return BookingAddon.query.filter_by(booking_id=booking_id).all()

    def update_addon(self, addon: BookingAddon) -> BookingAddon:
        """Commit changes the Service already applied to `addon`."""
        try:
            db.session.commit()
            return addon
        except Exception:
            db.session.rollback()
            raise

    def delete_addon(self, addon: BookingAddon) -> bool:
        """Delete the given booking add-on row. Returns True on success."""
        try:
            db.session.delete(addon)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
