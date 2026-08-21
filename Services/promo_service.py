# Services/promo_service.py
#
# Business logic for promo codes (vouchers). This service deliberately does
# NOT do the "apply promo to a booking" workflow — that belongs to the later
# booking workflow phase, which will create a PromoCodeUsage row and bump
# `used_count`. Here we just CRUD the PromoCode rows themselves.

from DAO import PromoCodeDAO
from models.promo_code import PromoCode
from api.serializers import promo_code_to_dict
from Services._result import ok, fail

# Allowed discount_type values per the design. We keep this as a simple
# module-level list so it's easy to read/change.
ALLOWED_DISCOUNT_TYPES = ("percentage", "fixed")


class PromoCodeService:
    def __init__(self):
        self.promo_dao = PromoCodeDAO()

    # ---------------- CREATE ----------------
    def create_promo(self, data: dict) -> dict:
        code = data.get("code")
        discount_type = data.get("discount_type")
        discount_value = data.get("discount_value")

        if not code or (isinstance(code, str) and not code.strip()):
            return fail("Missing required field: code", 400)
        if discount_type not in ALLOWED_DISCOUNT_TYPES:
            return fail(
                f"discount_type must be one of {list(ALLOWED_DISCOUNT_TYPES)}",
                400,
            )
        if discount_value is None:
            return fail("Missing required field: discount_value", 400)

        # uniqueness check
        if self.promo_dao.get_promo_by_code(code) is not None:
            return fail("Promo code already exists", 409)

        promo = PromoCode(
            code=code,
            description=data.get("description"),
            discount_type=discount_type,
            discount_value=discount_value,
            minimum_booking_amount=data.get("minimum_booking_amount", 0.00),
            max_uses=data.get("max_uses"),
            valid_from=data.get("valid_from"),
            valid_until=data.get("valid_until"),
            is_active=bool(data.get("is_active", True)),
        )
        try:
            saved = self.promo_dao.create_promo(promo)
        except Exception:
            return fail("Could not create promo code", 500)
        return ok("Promo code created", promo_code_to_dict(saved), status=201)

    # ---------------- READ ----------------
    def get_promo_by_id(self, promo_id: int) -> dict:
        p = self.promo_dao.get_promo_by_id(promo_id)
        if p is None:
            return fail("Promo code not found", 404)
        return ok("Promo code retrieved", promo_code_to_dict(p))

    def get_promo_by_code(self, code: str) -> dict:
        if not code:
            return fail("code is required", 400)
        p = self.promo_dao.get_promo_by_code(code)
        if p is None:
            return fail("Promo code not found", 404)
        return ok("Promo code retrieved", promo_code_to_dict(p))

    def get_all_promos(self) -> dict:
        promos = self.promo_dao.get_all_promos()
        return ok("Promo codes retrieved", [promo_code_to_dict(p) for p in promos])

    # ---------------- UPDATE ----------------
    def update_promo(self, promo_id: int, data: dict) -> dict:
        p = self.promo_dao.get_promo_by_id(promo_id)
        if p is None:
            return fail("Promo code not found", 404)

        if "code" in data:
            existing = self.promo_dao.get_promo_by_code(data["code"])
            if existing is not None and existing.id != p.id:
                return fail("Promo code already in use", 409)
            p.code = data["code"]
        if "discount_type" in data:
            if data["discount_type"] not in ALLOWED_DISCOUNT_TYPES:
                return fail(
                    f"discount_type must be one of {list(ALLOWED_DISCOUNT_TYPES)}",
                    400,
                )
            p.discount_type = data["discount_type"]

        for field in [
            "description", "discount_value", "minimum_booking_amount",
            "max_uses", "valid_from", "valid_until",
        ]:
            if field in data:
                setattr(p, field, data[field])
        if "is_active" in data:
            p.is_active = bool(data["is_active"])

        try:
            self.promo_dao.update_promo(p)
        except Exception:
            return fail("Could not update promo code", 500)
        return ok("Promo code updated", promo_code_to_dict(p))

    # ---------------- DELETE ----------------
    def delete_promo(self, promo_id: int) -> dict:
        p = self.promo_dao.get_promo_by_id(promo_id)
        if p is None:
            return fail("Promo code not found", 404)
        try:
            self.promo_dao.delete_promo(p)
        except Exception:
            return fail("Could not delete promo code", 500)
        return ok("Promo code deleted")
