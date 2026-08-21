# DAO/promo_code_usage_dao.py
#
# PromoCodeUsageDAO — Data Access Object for the `promo_code_usages` table.
# A PromoCodeUsage is an audit record of a promo code being used on a booking.

from app import db
from models.promo_code_usage import PromoCodeUsage


class PromoCodeUsageDAO:
    """Database operations for the PromoCodeUsage model."""

    def create_usage(self, usage: PromoCodeUsage) -> PromoCodeUsage:
        """Insert one new promo usage record (created when a booking is
        confirmed with a promo applied)."""
        try:
            db.session.add(usage)
            db.session.commit()
            return usage
        except Exception:
            db.session.rollback()
            raise

    def get_usage_by_id(self, usage_id: int) -> PromoCodeUsage | None:
        """Load one usage record by its primary key."""
        return db.session.get(PromoCodeUsage, usage_id)

    def get_usages_by_promo(self, promo_code_id: int) -> list[PromoCodeUsage]:
        """Return every usage of a given promo code (audit trail)."""
        return PromoCodeUsage.query.filter_by(promo_code_id=promo_code_id).all()

    def get_usages_by_user(self, user_id: int) -> list[PromoCodeUsage]:
        """Return every promo usage by a given user.

        Useful for the Service to enforce a one-use-per-user rule (business).
        """
        return PromoCodeUsage.query.filter_by(user_id=user_id).all()

    def get_usage_by_booking(self, booking_id: int) -> PromoCodeUsage | None:
        """Return the (at most one) promo usage for a given booking."""
        return PromoCodeUsage.query.filter_by(booking_id=booking_id).first()

    def update_usage(self, usage: PromoCodeUsage) -> PromoCodeUsage:
        """Commit changes the Service already applied to `usage`."""
        try:
            db.session.commit()
            return usage
        except Exception:
            db.session.rollback()
            raise

    def delete_usage(self, usage: PromoCodeUsage) -> bool:
        """Delete the given usage row. Returns True on success."""
        try:
            db.session.delete(usage)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
