# tests/unit/test_promo_service.py
#
# Pure unit tests for PromoCodeService with mocked PromoCodeDAO and PromoCodeUsageDAO.
# WHY: Promo codes offer percentage and fixed-amount discounts.
# Must enforce validity windows (valid_from/valid_until), minimum order subtotals, and usage limits.

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from Services.promo_service import PromoCodeService as PromoService
from models.promo_code import PromoCode


@pytest.mark.unit
class TestPromoService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.promo_service = PromoService()
        self.mock_promo_dao = MagicMock()
        self.mock_usage_dao = MagicMock()

        self.promo_service.promo_dao = self.mock_promo_dao
        self.promo_service.usage_dao = self.mock_usage_dao

    def test_validate_valid_percentage_promo(self):
        """WHY: Valid percentage discount computes exact percentage off subtotal."""
        promo = PromoCode(
            id=1, code="SUMMER10", discount_type="percentage", discount_value=10.00,
            minimum_booking_amount=50.00, is_active=True,
            valid_from=datetime.utcnow() - timedelta(days=5),
            valid_until=datetime.utcnow() + timedelta(days=5),
            max_uses=100, used_count=5
        )
        self.mock_promo_dao.get_promo_by_code.return_value = promo
        self.mock_usage_dao.get_usages_by_user.return_value = []

        res = self.promo_service.validate_and_calculate_discount("SUMMER10", user_id=None, order_subtotal=200.00)
        assert res["success"] is True
        assert res["data"]["discount_amount"] == 20.00

    def test_validate_valid_fixed_discount_promo(self):
        """WHY: Valid fixed amount discount computes exact fixed dollar discount."""
        promo = PromoCode(
            id=2, code="FLAT25", discount_type="fixed", discount_value=25.00,
            minimum_booking_amount=100.00, is_active=True,
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=1),
            max_uses=50, used_count=2
        )
        self.mock_promo_dao.get_promo_by_code.return_value = promo
        self.mock_usage_dao.get_usages_by_user.return_value = []

        res = self.promo_service.validate_and_calculate_discount("FLAT25", user_id=None, order_subtotal=120.00)
        assert res["success"] is True
        assert res["data"]["discount_amount"] == 25.00

    @pytest.mark.parametrize("scenario, amount, expected_msg", [
        ("none", 100.00, "Invalid promo code"),
        ("inactive", 100.00, "inactive"),
        ("expired", 100.00, "expired"),
        ("future", 100.00, "not yet valid"),
        ("highmin", 100.00, "Minimum booking amount"),
        ("maxed", 100.00, "usage limit"),
    ])
    def test_validate_promo_invalid_scenarios(self, scenario, amount, expected_msg):
        """WHY: Parameterized validation guarantees all boundary error states return clean 400 messages."""
        now = datetime.utcnow()
        if scenario == "none":
            promo_obj = None
        elif scenario == "inactive":
            promo_obj = PromoCode(id=10, code="INACTIVE", is_active=False, valid_from=now-timedelta(days=1), valid_until=now+timedelta(days=1))
        elif scenario == "expired":
            promo_obj = PromoCode(id=11, code="EXPIRED", is_active=True, valid_from=now-timedelta(days=10), valid_until=now-timedelta(days=1))
        elif scenario == "future":
            promo_obj = PromoCode(id=12, code="FUTURE", is_active=True, valid_from=now+timedelta(days=2), valid_until=now+timedelta(days=10))
        elif scenario == "highmin":
            promo_obj = PromoCode(id=13, code="HIGHMIN", is_active=True, minimum_booking_amount=200.00, valid_from=now-timedelta(days=1), valid_until=now+timedelta(days=1))
        elif scenario == "maxed":
            promo_obj = PromoCode(id=14, code="MAXED", is_active=True, max_uses=5, used_count=5, valid_from=now-timedelta(days=1), valid_until=now+timedelta(days=1))

        self.mock_usage_dao.get_usages_by_user.return_value = []
        self.mock_promo_dao.get_promo_by_code.return_value = promo_obj

        code = promo_obj.code if promo_obj else "NONE"
        res = self.promo_service.validate_and_calculate_discount(code, user_id=None, order_subtotal=amount)
        assert res["success"] is False
        assert expected_msg.lower() in res["message"].lower()
