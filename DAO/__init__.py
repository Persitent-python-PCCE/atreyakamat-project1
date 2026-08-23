# DAO (Data Access Object) package for SeatMeUp.
#
# Each file in this folder handles database operations for ONE model.
# For example, user_dao.py only talks to the `users` table.
#
# This file lists every DAO class so it can be imported cleanly:
#
#     from DAO import UserDAO, EventDAO, BookingDAO
#
# We deliberately do NOT use a generic BaseDAO or abstract repository pattern.
# Each DAO is written explicitly and is easy to read on its own.

from .user_dao import UserDAO
from .category_dao import CategoryDAO
from .venue_dao import VenueDAO
from .event_dao import EventDAO
from .seat_dao import SeatDAO
from .event_addon_dao import EventAddonDAO
from .seat_hold_dao import SeatHoldDAO
from .booking_dao import BookingDAO
from .booking_item_dao import BookingItemDAO
from .booking_addon_dao import BookingAddonDAO
from .promo_code_dao import PromoCodeDAO
from .promo_code_usage_dao import PromoCodeUsageDAO
from .reward_transaction_dao import RewardTransactionDAO
from .ticket_dao import TicketDAO
from .ticket_verification_dao import TicketVerificationDAO
from .notification_dao import NotificationDAO
from .event_reschedule_dao import EventRescheduleDAO
from .uploaded_file_dao import UploadedFileDAO
from .email_log_dao import EmailLogDAO
from .analytics_dao import AnalyticsDAO

__all__ = [
    "UserDAO",
    "CategoryDAO",
    "VenueDAO",
    "EventDAO",
    "SeatDAO",
    "EventAddonDAO",
    "SeatHoldDAO",
    "BookingDAO",
    "BookingItemDAO",
    "BookingAddonDAO",
    "PromoCodeDAO",
    "PromoCodeUsageDAO",
    "RewardTransactionDAO",
    "TicketDAO",
    "TicketVerificationDAO",
    "NotificationDAO",
    "EventRescheduleDAO",
    "UploadedFileDAO",
    "EmailLogDAO",
    "AnalyticsDAO",
]
