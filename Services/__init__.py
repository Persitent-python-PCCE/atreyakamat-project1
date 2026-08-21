# Services package — business-logic layer for SeatMeUp.
#
# Each file in this folder contains ONE service class (e.g. UserService).
# A Service:
#   - takes plain Python arguments (dicts, ints, strings)
#   - never imports Flask / request / jsonify
#   - calls one or more DAOs to talk to the database
#   - applies business rules and combines results
#   - returns a plain dict shaped by Services/_result.py:
#       {"success": bool, "message": str, "data": ... optional, "status": int}
#
# The Controller (api/*_routes.py) then turns that dict into an HTTP response.

from .user_service import UserService
from .category_service import CategoryService
from .venue_service import VenueService
from .event_service import EventService
from .seat_service import SeatService
from .event_addon_service import EventAddonService
from .seat_hold_service import SeatHoldService
from .booking_service import BookingService
from .ticket_service import TicketService
from .promo_service import PromoCodeService
from .reward_service import RewardService
from .notification_service import NotificationService
from .event_reschedule_service import EventRescheduleService
from .uploaded_file_service import UploadedFileService
from .email_log_service import EmailLogService

__all__ = [
    "UserService",
    "CategoryService",
    "VenueService",
    "EventService",
    "SeatService",
    "EventAddonService",
    "SeatHoldService",
    "BookingService",
    "TicketService",
    "PromoCodeService",
    "RewardService",
    "NotificationService",
    "EventRescheduleService",
    "UploadedFileService",
    "EmailLogService",
]
