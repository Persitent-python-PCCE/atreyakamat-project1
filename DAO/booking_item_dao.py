# DAO/booking_item_dao.py
#
# BookingItemDAO — Data Access Object for the `booking_items` table.
# A BookingItem is one line in a booking (a seat ticket, or a quantity).

from app import db
from models.booking_item import BookingItem


class BookingItemDAO:
    """Database operations for the BookingItem model."""

    def create_item(self, item: BookingItem) -> BookingItem:
        """Insert one new booking item row."""
        try:
            db.session.add(item)
            db.session.commit()
            return item
        except Exception:
            db.session.rollback()
            raise

    def create_items_bulk(self, items: list[BookingItem]) -> list[BookingItem]:
        """Insert many booking items in one transaction (all-or-nothing)."""
        try:
            for i in items:
                db.session.add(i)
            db.session.commit()
            return items
        except Exception:
            db.session.rollback()
            raise

    def get_item_by_id(self, item_id: int) -> BookingItem | None:
        """Load one booking item by its primary key."""
        return db.session.get(BookingItem, item_id)

    def get_items_by_booking(self, booking_id: int) -> list[BookingItem]:
        """Return every item that belongs to a given booking."""
        return BookingItem.query.filter_by(booking_id=booking_id).all()

    def get_items_by_seat(self, seat_id: int) -> list[BookingItem]:
        """Return every booking item that references a given seat.

        Useful for the Service to check whether a seat has already been sold
        (and is therefore unavailable).
        """
        return BookingItem.query.filter_by(seat_id=seat_id).all()

    def update_item(self, item: BookingItem) -> BookingItem:
        """Commit changes the Service already applied to `item`."""
        try:
            db.session.commit()
            return item
        except Exception:
            db.session.rollback()
            raise

    def delete_item(self, item: BookingItem) -> bool:
        """Delete the given booking item row. Returns True on success."""
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
