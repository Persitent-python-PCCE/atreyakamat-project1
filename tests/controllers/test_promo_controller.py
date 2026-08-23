# tests/controllers/test_promo_controller.py
#
# Controller tests for Promo Code API endpoints (/api/promos/*).
# WHY: Verifies promo code discount calculation endpoint without placing an order.

import pytest
from datetime import datetime, timedelta, timezone
from models.promo_code import PromoCode


@pytest.mark.controller
class TestPromoController:
    def test_validate_promo_code_api(self, client, db_session):
        """WHY: Validates promo code and returns exact calculated discount amount."""
        promo = PromoCode(
            code="SUMMER25",
            discount_type="percentage",
            discount_value=25.00,
            minimum_booking_amount=50.00,
            valid_from=datetime.now(timezone.utc) - timedelta(days=1),
            valid_until=datetime.now(timezone.utc) + timedelta(days=30),
            is_active=True,
        )
        db_session.add(promo)
        db_session.commit()

        res = client.post("/api/promos/validate", json={"code": "SUMMER25", "amount": 100.0})
        assert res.status_code == 200
        assert res.get_json()["data"]["discount_amount"] == 25.00
