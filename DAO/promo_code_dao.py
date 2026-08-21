# DAO/promo_code_dao.py
#
# PromoCodeDAO — Data Access Object for the `promo_codes` table.
# A promo code is a discount voucher customers can apply at checkout.

from app import db
from models.promo_code import PromoCode


class PromoCodeDAO:
    """Database operations for the PromoCode model."""

    def create_promo(self, promo: PromoCode) -> PromoCode:
        """Insert a new promo code row."""
        try:
            db.session.add(promo)
            db.session.commit()
            return promo
        except Exception:
            db.session.rollback()
            raise

    def get_promo_by_id(self, promo_id: int) -> PromoCode | None:
        """Load one promo code by its primary key."""
        return db.session.get(PromoCode, promo_id)

    def get_promo_by_code(self, code: str) -> PromoCode | None:
        """Look up a promo code by the code string customers type in.

        `code` is unique on the model, so .first() gives the only match.
        """
        return PromoCode.query.filter_by(code=code).first()

    def get_all_promos(self) -> list[PromoCode]:
        """Return every promo code in the database."""
        return PromoCode.query.all()

    def update_promo(self, promo: PromoCode) -> PromoCode:
        """Commit changes the Service already applied to `promo`."""
        try:
            db.session.commit()
            return promo
        except Exception:
            db.session.rollback()
            raise

    def delete_promo(self, promo: PromoCode) -> bool:
        """Delete the given promo row. Returns True on success."""
        try:
            db.session.delete(promo)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
