# tests/integration/test_swagger.py
#
# Integration tests for Swagger / OpenAPI documentation.
# WHY: Ensures /apidocs/ and /apispec_1.json endpoints are healthy,
# the OpenAPI specification renders with valid JSON, security definitions exist,
# and all core REST API endpoints are registered and documented.

import pytest


@pytest.mark.integration
class TestSwaggerDocs:
    def test_swagger_ui_endpoint_returns_200(self, client):
        """WHY: Verifies /apidocs/ renders successfully for developers and API consumers."""
        res = client.get("/apidocs/")
        assert res.status_code == 200
        assert b"swagger" in res.data.lower() or b"apidocs" in res.data.lower()

    def test_swagger_json_spec_returns_200_and_valid_structure(self, client):
        """WHY: Verifies /apispec_1.json is served with complete OpenAPI 2.0 structure."""
        res = client.get("/apispec_1.json")
        assert res.status_code == 200
        spec = res.get_json()

        assert spec is not None
        assert spec.get("swagger") == "2.0"
        assert "SeatMeUp" in spec.get("info", {}).get("title", "")
        assert "paths" in spec
        assert "definitions" in spec

    def test_swagger_security_definitions_configured(self, client):
        """WHY: Verifies JWT Bearer token authentication scheme is exposed for Swagger UI Authorize button."""
        res = client.get("/apispec_1.json")
        spec = res.get_json()

        sec_defs = spec.get("securityDefinitions", {})
        assert "Bearer" in sec_defs
        assert sec_defs["Bearer"]["type"] == "apiKey"
        assert sec_defs["Bearer"]["in"] == "header"
        assert sec_defs["Bearer"]["name"] == "Authorization"

    def test_swagger_expected_tags_present(self, client):
        """WHY: Verifies all major domain groups are present in tags."""
        res = client.get("/apispec_1.json")
        spec = res.get_json()

        tag_names = {t["name"] for t in spec.get("tags", [])}
        expected_tags = {
            "Authentication",
            "Users",
            "Categories",
            "Venues",
            "Events",
            "Seats",
            "Seat Holds",
            "Bookings",
            "Promo Codes",
            "Tickets",
            "Ticket Verification",
            "Notifications",
            "Event Rescheduling",
            "Admin Analytics",
        }
        for tag in expected_tags:
            assert tag in tag_names, f"Missing expected tag: {tag}"

    def test_swagger_core_paths_documented(self, client):
        """WHY: Verifies all essential API routes are documented in paths."""
        res = client.get("/apispec_1.json")
        spec = res.get_json()
        paths = spec.get("paths", {})

        expected_endpoints = [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/me",
            "/api/events",
            "/api/events/search",
            "/api/venues",
            "/api/categories",
            "/api/events/{event_id}/seats/{seat_id}/hold",
            "/api/events/{event_id}/seats/{seat_id}/release",
            "/api/checkout/preview",
            "/api/checkout/confirm",
            "/api/bookings/my",
            "/api/promos/validate",
            "/api/tickets/verify",
            "/api/admin/analytics",
            "/api/admin/events/{event_id}/reschedule",
        ]
        for path in expected_endpoints:
            assert path in paths, f"Missing documented endpoint: {path}"

    def test_swagger_core_definitions_present(self, client):
        """WHY: Verifies model schemas are available for request and response definitions."""
        res = client.get("/apispec_1.json")
        spec = res.get_json()
        definitions = spec.get("definitions", {})

        expected_schemas = [
            "User",
            "Category",
            "Venue",
            "Event",
            "Seat",
            "SeatHold",
            "Booking",
            "PromoCode",
            "Ticket",
            "TicketVerification",
            "Notification",
            "EventReschedule",
            "AnalyticsSummary",
        ]
        for schema in expected_schemas:
            assert schema in definitions, f"Missing schema definition: {schema}"
