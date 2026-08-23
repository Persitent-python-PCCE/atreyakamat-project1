# Controller/web_customer_controller.py
#
# WebCustomerController — handles customer dashboard, bookings, and profile pages.
#
# Routes:
#   GET /dashboard
#   GET /my-bookings
#   GET /profile

from flask import Blueprint, render_template, redirect, url_for
from Services.user_service import UserService
from Services.booking_service import BookingService
from Services.notification_service import NotificationService
from Services.event_service import EventService
from Controller.auth_guards import get_current_user_info

web_customer_bp = Blueprint("web_customer_bp", __name__)
user_service = UserService()
booking_service = BookingService()
notification_service = NotificationService()
event_service = EventService()


@web_customer_bp.route("/dashboard")
def customer_dashboard():
    """Render customer dashboard with recent bookings and notifications."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login"))

    # Fetch user data through services
    user_res = user_service.get_user_by_id(current_user["id"])
    user = user_res.get("data", {}) if user_res.get("success") else current_user

    # Fetch bookings
    bookings_res = booking_service.get_user_bookings(current_user["id"])
    bookings = bookings_res.get("data", []) if bookings_res.get("success") else []

    # Fetch notifications
    notifs_res = notification_service.get_user_notifications(current_user["id"])
    notifications = notifs_res.get("data", []) if notifs_res.get("success") else []

    return render_template(
        "customer/dashboard.html",
        user=user,
        bookings=bookings,
        notifications=notifications,
    )


@web_customer_bp.route("/my-bookings")
def my_bookings():
    """Redirect to the unified My Bookings page."""
    return redirect(url_for("web_event_bp.my_bookings"))


@web_customer_bp.route("/profile")
def profile():
    """Render customer profile page."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login"))

    user_res = user_service.get_user_by_id(current_user["id"])
    user = user_res.get("data", {}) if user_res.get("success") else current_user

    return render_template("customer/profile.html", user=user)
