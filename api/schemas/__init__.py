# api/schemas/__init__.py
#
# Central export module for Marshmallow validation & serialization schemas.

from .common_schema import validate_payload
from .auth_schema import RegisterRequestSchema, LoginRequestSchema
from .user_schema import UserCreateRequestSchema, UserUpdateRequestSchema, UserResponseSchema
from .category_schema import CategoryCreateRequestSchema, CategoryUpdateRequestSchema, CategoryResponseSchema
from .venue_schema import VenueCreateRequestSchema, VenueUpdateRequestSchema, VenueResponseSchema
from .event_schema import EventCreateRequestSchema, EventUpdateRequestSchema, EventResponseSchema
from .seat_schema import SeatCreateRequestSchema, SeatResponseSchema
from .seat_hold_schema import SeatHoldResponseSchema
from .booking_schema import CheckoutPreviewRequestSchema, CheckoutConfirmRequestSchema, BookingResponseSchema
from .promo_schema import PromoValidateRequestSchema, PromoCreateRequestSchema, PromoUpdateRequestSchema, PromoResponseSchema
from .ticket_schema import TicketVerifyRequestSchema, TicketResponseSchema, TicketVerificationResponseSchema
from .notification_schema import NotificationCreateRequestSchema, NotificationResponseSchema
from .reschedule_schema import EventRescheduleRequestSchema, EventRescheduleResponseSchema
from .analytics_schema import AnalyticsSummaryResponseSchema

__all__ = [
    "validate_payload",
    "RegisterRequestSchema",
    "LoginRequestSchema",
    "UserCreateRequestSchema",
    "UserUpdateRequestSchema",
    "UserResponseSchema",
    "CategoryCreateRequestSchema",
    "CategoryUpdateRequestSchema",
    "CategoryResponseSchema",
    "VenueCreateRequestSchema",
    "VenueUpdateRequestSchema",
    "VenueResponseSchema",
    "EventCreateRequestSchema",
    "EventUpdateRequestSchema",
    "EventResponseSchema",
    "SeatCreateRequestSchema",
    "SeatResponseSchema",
    "SeatHoldResponseSchema",
    "CheckoutPreviewRequestSchema",
    "CheckoutConfirmRequestSchema",
    "BookingResponseSchema",
    "PromoValidateRequestSchema",
    "PromoCreateRequestSchema",
    "PromoUpdateRequestSchema",
    "PromoResponseSchema",
    "TicketVerifyRequestSchema",
    "TicketResponseSchema",
    "TicketVerificationResponseSchema",
    "NotificationCreateRequestSchema",
    "NotificationResponseSchema",
    "EventRescheduleRequestSchema",
    "EventRescheduleResponseSchema",
    "AnalyticsSummaryResponseSchema",
]
