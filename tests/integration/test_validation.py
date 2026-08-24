# tests/integration/test_validation.py
#
# Integration tests for Controller-level Marshmallow API request validation.
# WHY: Proves that malformed, invalid, or missing request data is intercepted and
# rejected with HTTP 400 Bad Request and structured validation messages before
# reaching Service or DAO execution.

import pytest


@pytest.mark.integration
class TestControllerValidation:
    def test_post_register_with_invalid_email_returns_400(self, client):
        """WHY: Verifies register controller blocks malformed email before AuthService."""
        res = client.post(
            "/api/auth/register",
            json={
                "name": "Jane",
                "email": "not-a-valid-email",
                "password": "Password123!",
            },
        )
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False
        assert payload["message"] == "Validation failed"
        assert "email" in payload.get("data", {})

    def test_post_event_with_missing_fields_returns_400(self, client, auth_headers_admin):
        """WHY: Verifies event creation controller blocks incomplete payloads."""
        res = client.post(
            "/api/events",
            headers=auth_headers_admin,
            json={"title": "Incomplete Event"},
        )
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False
        assert payload["message"] == "Validation failed"
        assert "category_id" in payload.get("data", {})
        assert "venue_id" in payload.get("data", {})

    def test_post_checkout_confirm_with_invalid_quantity_returns_400(
        self, client, auth_headers_customer, event
    ):
        """WHY: Verifies checkout controller blocks zero/negative ticket quantities."""
        res = client.post(
            "/api/checkout/confirm",
            headers=auth_headers_customer,
            json={
                "event_id": event.id,
                "quantity": -3,
            },
        )
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False
        assert payload["message"] == "Validation failed"
        assert "quantity" in payload.get("data", {})

    def test_post_ticket_verify_with_missing_token_returns_400(self, client):
        """WHY: Verifies ticket verification controller rejects requests missing ticket_token."""
        res = client.post("/api/tickets/verify", json={})
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False

    def test_post_admin_reschedule_with_missing_password_returns_400(
        self, client, auth_headers_admin, event
    ):
        """WHY: Verifies reschedule controller requires admin password confirmation."""
        res = client.post(
            f"/api/admin/events/{event.id}/reschedule",
            headers=auth_headers_admin,
            json={
                "new_event_date": "2026-12-25",
                "new_start_time": "20:00",
                "reason": "Holiday shift",
            },
        )
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False
        assert payload["message"] == "Validation failed"
        assert "password" in payload.get("data", {})

    def test_post_venue_create_with_invalid_capacity_returns_400(
        self, client, auth_headers_admin
    ):
        """WHY: Verifies venue controller blocks zero/negative capacities."""
        res = client.post(
            "/api/venues",
            headers=auth_headers_admin,
            json={
                "name": "Invalid Venue",
                "address": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "capacity": -100,
            },
        )
        assert res.status_code == 400
        payload = res.get_json()
        assert payload["success"] is False
        assert payload["message"] == "Validation failed"
        assert "capacity" in payload.get("data", {})
