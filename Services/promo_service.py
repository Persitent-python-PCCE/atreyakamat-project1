# Services/promo_service.py
#
# Business logic for promo codes (vouchers) and discount validation.

from datetime import datetime

from DAO import PromoCodeDAO, PromoCodeUsageDAO
from models.promo_code import PromoCode
from api.serializers import promo_code_to_dict
from Services._result import ok, fail

ALLOWED_DISCOUNT_TYPES = ("percentage", "fixed")


class PromoCodeService:
    def __init__(self):
        self.promo_dao = PromoCodeDAO()
        self.usage_dao = PromoCodeUsageDAO()

    # ---------------- VALIDATION & DISCOUNT CALCULATION ----------------
    def validate_and_calculate_discount(
        self, code: str, user_id: int | None, order_subtotal: float
    ) -> dict:
        """Validate a promo code for a given user and order amount, and calculate the discount."""
        if not code or not code.strip():
            return fail("Promo code is required", 400)

        cleaned_code = code.strip().upper()
        promo = self.promo_dao.get_promo_by_code(cleaned_code)
        if promo is None:
            return fail("Invalid promo code", 404)

        if not promo.is_active:
            return fail("Promo code is currently inactive", 400)

        now = datetime.utcnow()
        if promo.valid_from and now < promo.valid_from:
            return fail("Promo code is not yet valid", 400)

        if promo.valid_until and now > promo.valid_until:
            return fail("Promo code has expired", 400)

        if promo.max_uses is not None and promo.used_count >= promo.max_uses:
            return fail("Promo code usage limit has been reached", 400)

        min_amount = float(promo.minimum_booking_amount or 0.0)
        if order_subtotal < min_amount:
            return fail(
                f"Minimum booking amount of ${min_amount:.2f} is required to apply this promo code",
                400,
            )

        if user_id is not None:
            user_usages = self.usage_dao.get_usages_by_user(user_id)
            already_used = any(u.promo_code_id == promo.id for u in user_usages)
            if already_used:
                return fail("You have already used this promo code", 400)

        # Calculate discount
        val = float(promo.discount_value)
        if promo.discount_type == "percentage":
            discount = round(order_subtotal * (val / 100.0), 2)
        elif promo.discount_type == "fixed":
            discount = round(val, 2)
        else:
            discount = 0.0

        # Cannot discount more than order subtotal
        discount = min(discount, order_subtotal)

        return ok(
            "Promo code applied successfully",
            {
                "promo_id": promo.id,
                "code": promo.code,
                "description": promo.description,
                "discount_type": promo.discount_type,
                "discount_value": float(promo.discount_value),
                "discount_amount": discount,
            },
        )

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

        code_upper = code.strip().upper()
        if self.promo_dao.get_promo_by_code(code_upper) is not None:
            return fail("Promo code already exists", 409)

        promo = PromoCode(
            code=code_upper,
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
        p = self.promo_dao.get_promo_by_code(code.strip().upper())
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
            code_upper = data["code"].strip().upper()
            existing = self.promo_dao.get_promo_by_code(code_upper)
            if existing is not None and existing.id != p.id:
                return fail("Promo code already in use", 409)
            p.code = code_upper
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
