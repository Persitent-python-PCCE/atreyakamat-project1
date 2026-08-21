# Controller package — HTTP routing and request/response layer.
#
# Each controller defines Blueprints and route handlers that:
#   1. Accept the incoming HTTP request
#   2. Extract and validate parameters
#   3. Delegate work to the appropriate Service
#   4. Return standard JSON responses or render Jinja2 templates

from .home_controller import home_bp
from .auth_controller import api_auth_bp, web_auth_bp, auth_service
from .user_controller import user_bp, user_service
from .category_controller import category_bp, category_service
from .venue_controller import venue_bp, venue_service
from .event_controller import event_bp, event_service
from .seat_controller import seat_bp, seat_service
from .booking_controller import booking_bp, booking_service
from .ticket_controller import ticket_bp, ticket_service
from .notification_controller import notification_bp, notification_service
from .promo_controller import promo_bp, promo_service
from .web_event_controller import web_event_bp
from .web_customer_controller import web_customer_bp
from .web_admin_controller import web_admin_bp

__all__ = [
    "home_bp",
    "api_auth_bp",
    "web_auth_bp",
    "auth_service",
    "user_bp",
    "user_service",
    "category_bp",
    "category_service",
    "venue_bp",
    "venue_service",
    "event_bp",
    "event_service",
    "seat_bp",
    "seat_service",
    "booking_bp",
    "booking_service",
    "ticket_bp",
    "ticket_service",
    "notification_bp",
    "notification_service",
    "promo_bp",
    "promo_service",
    "web_event_bp",
    "web_customer_bp",
    "web_admin_bp",
]
