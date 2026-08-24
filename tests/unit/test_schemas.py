# tests/unit/test_schemas.py
#
# Unit tests for Marshmallow request validation and response serialization schemas.
# WHY: Validates field constraints, required types, value ranges, email format,
# cross-field validation, and safe data filtering before reaching business logic.

import pytest
from marshmallow import ValidationError

from api.schemas import (
    RegisterRequestSchema,
    LoginRequestSchema,
    UserCreateRequestSchema,
    UserUpdateRequestSchema,
    UserResponseSchema,
    CategoryCreateRequestSchema,
    VenueCreateRequestSchema,
    VenueUpdateRequestSchema,
    EventCreateRequestSchema,
    EventUpdateRequestSchema,
    EventResponseSchema,
    SeatCreateRequestSchema,
    CheckoutPreviewRequestSchema,
    CheckoutConfirmRequestSchema,
    PromoValidateRequestSchema,
    PromoCreateRequestSchema,
    TicketVerifyRequestSchema,
    EventRescheduleRequestSchema,
)


@pytest.mark.unit
class TestAuthSchemas:
    def test_valid_registration(self):
        """WHY: Verifies properly structured customer registration payload loads successfully."""
        data = {
            "name": "Jane Doe",
            "email": "jane@seatmeup.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "phone": "+1234567890",
            "role": "customer",
        }
        loaded = RegisterRequestSchema().load(data)
        assert loaded["name"] == "Jane Doe"
        assert loaded["email"] == "jane@seatmeup.com"

    def test_registration_missing_email_raises_validation_error(self):
        """WHY: Ensures missing email is rejected."""
        data = {"name": "Jane", "password": "pass"}
        with pytest.raises(ValidationError) as exc:
            RegisterRequestSchema().load(data)
        assert "email" in exc.value.messages

    @pytest.mark.parametrize("bad_email", ["not-an-email", "@missinguser.com", "missingdomain@"])
    def test_invalid_email_format_raises_validation_error(self, bad_email):
        """WHY: Ensures malformed email addresses are rejected."""
        data = {"name": "Jane", "email": bad_email, "password": "password123"}
        with pytest.raises(ValidationError) as exc:
            RegisterRequestSchema().load(data)
        assert "email" in exc.value.messages

    def test_registration_missing_password_raises_validation_error(self):
        """WHY: Ensures password is required."""
        data = {"name": "Jane", "email": "jane@seatmeup.com"}
        with pytest.raises(ValidationError) as exc:
            RegisterRequestSchema().load(data)
        assert "password" in exc.value.messages

    def test_password_confirmation_mismatch_raises_validation_error(self):
        """WHY: Enforces cross-field validation when confirm_password does not match password."""
        data = {
            "name": "Jane",
            "email": "jane@seatmeup.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword456!",
        }
        with pytest.raises(ValidationError) as exc:
            RegisterRequestSchema().load(data)
        assert "confirm_password" in exc.value.messages

    def test_valid_login_payload(self):
        """WHY: Verifies valid login credentials load cleanly."""
        data = {"email": "user@seatmeup.com", "password": "MySecretPassword"}
        loaded = LoginRequestSchema().load(data)
        assert loaded["email"] == "user@seatmeup.com"


@pytest.mark.unit
class TestUserSchemas:
    def test_user_serialization_excludes_password_hash(self):
        """WHY: Security guarantee that password_hash is never exposed in serialized User data."""
        user_dict = {
            "id": 1,
            "name": "Test User",
            "email": "user@seatmeup.com",
            "role": "customer",
            "reward_balance": 15.50,
            "password_hash": "scrypt:32768:8:1$verysecret$hash",
        }
        serialized = UserResponseSchema().dump(user_dict)
        assert "password_hash" not in serialized
        assert serialized["name"] == "Test User"
        assert serialized["reward_balance"] == 15.50


@pytest.mark.unit
class TestEventSchemas:
    def test_valid_event_creation(self):
        """WHY: Verifies complete and valid event creation schema passes."""
        data = {
            "title": "Summer Jazz Fest 2026",
            "category_id": 1,
            "venue_id": 2,
            "event_date": "2026-09-15",
            "start_time": "19:00",
            "base_price": 45.00,
            "status": "published",
        }
        loaded = EventCreateRequestSchema().load(data)
        assert loaded["title"] == "Summer Jazz Fest 2026"
        assert loaded["base_price"] == 45.00

    def test_missing_required_event_field_raises_error(self):
        """WHY: Ensures required event fields (title, category_id, venue_id, date, start_time) are checked."""
        data = {"title": "Missing details"}
        with pytest.raises(ValidationError) as exc:
            EventCreateRequestSchema().load(data)
        assert "category_id" in exc.value.messages
        assert "venue_id" in exc.value.messages
        assert "event_date" in exc.value.messages
        assert "start_time" in exc.value.messages

    def test_negative_event_price_raises_error(self):
        """WHY: Enforces non-negative pricing."""
        data = {
            "title": "Invalid Price Fest",
            "category_id": 1,
            "venue_id": 1,
            "event_date": "2026-09-15",
            "start_time": "19:00",
            "base_price": -10.00,
        }
        with pytest.raises(ValidationError) as exc:
            EventCreateRequestSchema().load(data)
        assert "base_price" in exc.value.messages


@pytest.mark.unit
class TestVenueSchemas:
    def test_valid_venue_creation(self):
        """WHY: Verifies valid venue payload loads correctly."""
        data = {
            "name": "Arena Central",
            "address": "123 Stadium Way",
            "city": "Austin",
            "state": "TX",
            "capacity": 5000,
            "venue_type": "seated",
        }
        loaded = VenueCreateRequestSchema().load(data)
        assert loaded["capacity"] == 5000
        assert loaded["venue_type"] == "seated"

    @pytest.mark.parametrize("bad_cap", [0, -1, -500])
    def test_invalid_venue_capacity_raises_error(self, bad_cap):
        """WHY: Ensures venue capacity must be a positive integer >= 1."""
        data = {
            "name": "Arena",
            "address": "123 St",
            "city": "Austin",
            "state": "TX",
            "capacity": bad_cap,
        }
        with pytest.raises(ValidationError) as exc:
            VenueCreateRequestSchema().load(data)
        assert "capacity" in exc.value.messages

    def test_invalid_venue_type_raises_error(self):
        """WHY: Enforces enum constraint on venue_type ('seated' or 'general')."""
        data = {
            "name": "Arena",
            "address": "123 St",
            "city": "Austin",
            "state": "TX",
            "capacity": 100,
            "venue_type": "virtual_metaverse",
        }
        with pytest.raises(ValidationError) as exc:
            VenueCreateRequestSchema().load(data)
        assert "venue_type" in exc.value.messages


@pytest.mark.unit
class TestBookingAndPromoSchemas:
    @pytest.mark.parametrize("bad_qty", [0, -1, -10])
    def test_zero_or_negative_booking_quantity_raises_error(self, bad_qty):
        """WHY: Ensures ticket purchase quantity must be >= 1."""
        data = {"event_id": 1, "quantity": bad_qty}
        with pytest.raises(ValidationError) as exc:
            CheckoutConfirmRequestSchema().load(data)
        assert "quantity" in exc.value.messages

    def test_invalid_promo_validation_payload_raises_error(self):
        """WHY: Ensures promo validation requires a valid code string."""
        data = {"amount": -20.0}
        with pytest.raises(ValidationError) as exc:
            PromoValidateRequestSchema().load(data)
        assert "code" in exc.value.messages
        assert "amount" in exc.value.messages

    def test_invalid_ticket_verification_payload(self):
        """WHY: Verifies TicketVerifyRequestSchema handles verification inputs."""
        loaded = TicketVerifyRequestSchema().load({"ticket_token": "TOK-12345", "mark_as_used": True})
        assert loaded["ticket_token"] == "TOK-12345"
        assert loaded["mark_as_used"] is True

    def test_invalid_reschedule_payload_raises_error(self):
        """WHY: Ensures event rescheduling requires new date, start time, reason, and admin password."""
        data = {"new_event_date": "2026-10-10"}
        with pytest.raises(ValidationError) as exc:
            EventRescheduleRequestSchema().load(data)
        assert "new_start_time" in exc.value.messages
        assert "password" in exc.value.messages
