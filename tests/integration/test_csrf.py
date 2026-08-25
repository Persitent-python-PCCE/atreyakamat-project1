# tests/integration/test_csrf.py
#
# Integration tests for CSRF Protection & Web Security Hardening.
# WHY: Ensures browser state-changing forms are protected against Cross-Site Request Forgery,
# missing or invalid CSRF tokens are rejected with friendly 400 errors,
# and JWT Bearer REST API endpoints remain completely unaffected.

import re
import pytest
from flask_jwt_extended import set_access_cookies


def extract_csrf_token(client, path="/login"):
    """Helper to fetch a web page and extract the rendered CSRF token."""
    res = client.get(path)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if not match:
        match = re.search(r'value="([^"]+)"\s+name="csrf_token"', html)
    if not match:
        match = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    assert match is not None, f"Could not find CSRF token on page {path}"
    return match.group(1)


@pytest.mark.integration
class TestCSRFProtection:
    def test_get_web_requests_remain_unaffected(self, client):
        """WHY: Verifies normal GET web browsing never requires or fails CSRF checks."""
        res_home = client.get("/")
        assert res_home.status_code == 200

        res_events = client.get("/events")
        assert res_events.status_code == 200

        res_login = client.get("/login")
        assert res_login.status_code == 200

        res_register = client.get("/register")
        assert res_register.status_code == 200

    def test_web_post_without_csrf_token_is_rejected(self, client):
        """WHY: Verifies web form POST without CSRF token is intercepted and returns 400 error."""
        res = client.post("/login", data={"email": "nobody@test.com", "password": "wrong"})
        assert res.status_code == 400
        assert b"CSRF validation failed" in res.data or b"csrf" in res.data.lower()

    def test_web_post_with_invalid_csrf_token_is_rejected(self, client):
        """WHY: Verifies forged or tampered CSRF tokens are strictly rejected."""
        res = client.post(
            "/login",
            data={
                "csrf_token": "malicious-forged-token-12345",
                "email": "nobody@test.com",
                "password": "wrong",
            },
        )
        assert res.status_code == 400
        assert b"CSRF validation failed" in res.data or b"csrf" in res.data.lower()

    def test_web_post_with_valid_csrf_token_is_accepted(self, client, customer_user):
        """WHY: Verifies legitimate browser users submitting valid CSRF tokens can log in."""
        token = extract_csrf_token(client, "/login")
        res = client.post(
            "/login",
            data={
                "csrf_token": token,
                "email": customer_user.email,
                "password": "CustPass123!",
            },
            follow_redirects=False,
        )
        # Login redirects to dashboard on success
        assert res.status_code == 302
        assert "/dashboard" in res.headers.get("Location", "")

    def test_web_registration_with_csrf_token_succeeds(self, client):
        """WHY: Verifies customer registration works end-to-end with CSRF protection."""
        token = extract_csrf_token(client, "/register")
        res = client.post(
            "/register",
            data={
                "csrf_token": token,
                "name": "New User CSRF",
                "email": "new_csrf_user@seatmeup.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=False,
        )
        assert res.status_code == 302

    def test_rest_api_jwt_bearer_requests_continue_to_work_without_csrf(
        self, client, auth_headers_customer, auth_headers_admin, event
    ):
        """WHY: Verifies REST API calls with Authorization header are exempted from HTML CSRF tokens."""
        # 1. Customer GET /api/auth/me
        res = client.get("/api/auth/me", headers=auth_headers_customer)
        assert res.status_code == 200
        assert res.get_json()["success"] is True

        # 2. Public API POST /api/auth/login
        res_login = client.post(
            "/api/auth/login",
            json={"email": "customer_fixture@seatmeup.com", "password": "CustPass123!"},
        )
        assert res_login.status_code == 200
        assert res_login.get_json()["success"] is True

        # 3. Admin GET /api/admin/analytics
        res_admin = client.get("/api/admin/analytics", headers=auth_headers_admin)
        assert res_admin.status_code == 200
        assert res_admin.get_json()["success"] is True

    def test_admin_event_create_and_delete_forms_require_csrf(self, client, app, admin_token, category, venue):
        """WHY: Ensures administrative event creation and deletion forms enforce CSRF."""
        client.set_cookie("access_token_cookie", admin_token)

        # 1. POST without CSRF is rejected
        res_fail = client.post(
            "/admin/events/create",
            data={
                "title": "CSRF Attack Event",
                "category_id": category.id,
                "venue_id": venue.id,
                "event_date": "2026-11-20",
                "start_time": "18:00",
                "base_price": 50.0,
            },
        )
        assert res_fail.status_code == 400

        # 2. POST with valid CSRF succeeds
        token = extract_csrf_token(client, "/admin/events/create")
        res_ok = client.post(
            "/admin/events/create",
            data={
                "csrf_token": token,
                "title": "Legitimate Admin Event",
                "category_id": category.id,
                "venue_id": venue.id,
                "event_date": "2026-11-20",
                "start_time": "18:00",
                "base_price": 50.0,
                "booking_open": "1",
                "requires_seats": "1",
            },
            follow_redirects=False,
        )
        assert res_ok.status_code == 302

    def test_event_rescheduling_form_requires_csrf(self, client, admin_token, event):
        """WHY: Verifies sensitive reschedule action is protected against CSRF."""
        client.set_cookie("access_token_cookie", admin_token)

        # POST without CSRF is rejected
        res_fail = client.post(
            f"/admin/events/{event.id}/reschedule",
            data={
                "new_event_date": "2026-12-01",
                "new_start_time": "20:00",
                "reason": "Security test",
                "password": "AdminPass123!",
            },
        )
        assert res_fail.status_code == 400

        # POST with CSRF succeeds
        token = extract_csrf_token(client, f"/admin/events/{event.id}/reschedule")
        res_ok = client.post(
            f"/admin/events/{event.id}/reschedule",
            data={
                "csrf_token": token,
                "new_event_date": "2026-12-01",
                "new_start_time": "20:00",
                "reason": "Security test with CSRF",
                "password": "AdminPass123!",
            },
            follow_redirects=False,
        )
        assert res_ok.status_code in (200, 302)

    def test_venue_crud_forms_require_csrf(self, client, admin_token, venue):
        """WHY: Verifies venue creation, editing, and deletion web forms require CSRF."""
        client.set_cookie("access_token_cookie", admin_token)

        # 1. Create venue without CSRF -> 400
        res_create_fail = client.post(
            "/admin/venues/create",
            data={"name": "Attacker Venue", "address": "123 Hack St", "city": "NYC", "state": "NY", "capacity": "100"},
        )
        assert res_create_fail.status_code == 400

        # 2. Create venue with CSRF -> 302
        token = extract_csrf_token(client, "/admin/venues/create")
        res_create_ok = client.post(
            "/admin/venues/create",
            data={
                "csrf_token": token,
                "name": "Secured Venue",
                "address": "456 Safe St",
                "city": "Boston",
                "state": "MA",
                "capacity": "250",
                "venue_type": "seated",
            },
            follow_redirects=False,
        )
        assert res_create_ok.status_code == 302

        # 3. Edit venue without CSRF -> 400
        res_edit_fail = client.post(
            f"/admin/venues/{venue.id}/edit",
            data={"name": "Modified Without CSRF", "address": venue.address, "city": venue.city, "state": venue.state, "capacity": "300"},
        )
        assert res_edit_fail.status_code == 400

        # 4. Delete venue without CSRF -> 400
        res_del_fail = client.post(f"/admin/venues/{venue.id}/delete")
        assert res_del_fail.status_code == 400

    def test_customer_cannot_bypass_rbac_with_valid_csrf(self, client, customer_token, event):
        """WHY: Verifies CSRF protection does not weaken RBAC (customer with valid CSRF still cannot access admin routes)."""
        client.set_cookie("access_token_cookie", customer_token)

        token = extract_csrf_token(client, "/login")
        res = client.post(
            f"/admin/events/{event.id}/delete",
            data={"csrf_token": token},
        )
        # Should be forbidden with 403
        assert res.status_code == 403
        assert b"permission" in res.data.lower() or b"forbidden" in res.data.lower()

    def test_booking_cancellation_web_form_requires_csrf(self, client, customer_token):
        """WHY: Verifies customer booking cancellation web form requires CSRF."""
        client.set_cookie("access_token_cookie", customer_token)

        # POST without CSRF -> 400
        res_fail = client.post("/bookings/999/cancel")
        assert res_fail.status_code == 400
        assert b"CSRF validation failed" in res_fail.data
