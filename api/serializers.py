# api/serializers.py
#
# Small helper functions that convert SQLAlchemy model objects into plain
# Python dictionaries. We need this because Flask's jsonify() cannot
# directly serialize a SQLAlchemy model object.
#
# Each function is named `to_dict_<model>` and takes ONE model instance.
# It returns a dict with only the simple fields (no relationships) — we
# intentionally keep API responses flat and beginner-friendly.
#
# IMPORTANT: these helpers only READ fields. They do NOT do any business
# logic, validation, or transformation beyond type-casting (e.g. converting
# a Decimal or datetime to a JSON-friendly string).

from datetime import date, datetime, time
from decimal import Decimal


# ---------- small internal helpers ----------

def _ser(value):
    """Convert a single value into something JSON-safe."""
    if value is None:
        return None
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        # use float for JSON; the Service can later decide on rounding
        return float(value)
    if isinstance(value, bool):
        return value
    return value


def ok(message, data=None, status=200):
    """Build a standard success response payload.

    Usage in a route:
        return jsonify(ok("User retrieved", user_dict)), 200
    """
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return payload


def err(message, status=400):
    """Build a standard error response payload (no `data` field)..

    Usage in a route:
        return jsonify(err("User not found", 404)), 404
    """
    return {"success": False, "message": message}


# ---------- per-model serializers ----------

def user_to_dict(user):
    """Serialize a User object to a plain dict."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": user.phone,
        "id_document": user.id_document,
        "reward_balance": _ser(user.reward_balance),
        "is_active": user.is_active,
        "created_at": _ser(user.created_at),
        "updated_at": _ser(user.updated_at),
    }


def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "created_at": _ser(category.created_at),
    }


def venue_to_dict(venue):
    return {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "capacity": venue.capacity,
        "venue_type": venue.venue_type,
        "created_at": _ser(venue.created_at),
        "updated_at": _ser(venue.updated_at),
    }


def event_to_dict(event):
    return {
        "id": event.id,
        "category_id": event.category_id,
        "venue_id": event.venue_id,
        "created_by": event.created_by,
        "title": event.title,
        "description": event.description,
        "event_date": _ser(event.event_date),
        "start_time": _ser(event.start_time),
        "end_time": _ser(event.end_time),
        "poster": event.poster,
        "booking_open": event.booking_open,
        "status": event.status,
        "requires_seats": event.requires_seats,
        "base_price": _ser(event.base_price),
        "created_at": _ser(event.created_at),
        "updated_at": _ser(event.updated_at),
    }


def seat_to_dict(seat):
    return {
        "id": seat.id,
        "venue_id": seat.venue_id,
        "seat_number": seat.seat_number,
        "section_name": seat.section_name,
        "seat_type": seat.seat_type,
        "price": _ser(seat.price),
        "is_active": seat.is_active,
        "created_at": _ser(seat.created_at),
    }


def booking_to_dict(booking):
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "event_id": booking.event_id,
        "booking_reference": booking.booking_reference,
        "total_amount": _ser(booking.total_amount),
        "discount_amount": _ser(booking.discount_amount),
        "cashback_amount": _ser(booking.cashback_amount),
        "status": booking.status,
        "booked_at": _ser(booking.booked_at),
        "cancelled_at": _ser(booking.cancelled_at),
    }


def ticket_to_dict(ticket):
    return {
        "id": ticket.id,
        "booking_id": ticket.booking_id,
        "ticket_token": ticket.ticket_token,
        "ticket_status": ticket.ticket_status,
        "qr_data": ticket.qr_data,
        "issued_at": _ser(ticket.issued_at),
        "used_at": _ser(ticket.used_at),
        "expired_at": _ser(ticket.expired_at),
    }


def ticket_verification_to_dict(v):
    return {
        "id": v.id,
        "ticket_id": v.ticket_id,
        "verification_status": v.verification_status,
        "verified_at": _ser(v.verified_at),
    }


def notification_to_dict(n):
    return {
        "id": n.id,
        "user_id": n.user_id,
        "title": n.title,
        "message": n.message,
        "notification_type": n.notification_type,
        "is_read": n.is_read,
        "created_at": _ser(n.created_at),
    }


def promo_code_to_dict(p):
    return {
        "id": p.id,
        "code": p.code,
        "description": p.description,
        "discount_type": p.discount_type,
        "discount_value": _ser(p.discount_value),
        "minimum_booking_amount": _ser(p.minimum_booking_amount),
        "max_uses": p.max_uses,
        "used_count": p.used_count,
        "valid_from": _ser(p.valid_from),
        "valid_until": _ser(p.valid_until),
        "is_active": p.is_active,
        "created_at": _ser(p.created_at),
    }
