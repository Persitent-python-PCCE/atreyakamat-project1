# api/ticket_routes.py
#
# CONTROLLER for tickets and ticket verification.
#
# URL prefix for this blueprint is `/api` (see api/__init__.py), so the full
# paths are:
#
#   GET  /api/tickets/<token>                get a ticket by its unique token
#   GET  /api/bookings/<booking_id>/ticket   get the ticket of a booking
#   POST /api/tickets/<token>/verify         record a verification attempt

from flask import Blueprint, request, jsonify

from Services import TicketService

ticket_bp = Blueprint("ticket_bp", __name__)
ticket_service = TicketService()


@ticket_bp.get("/tickets/<string:token>")
def get_ticket_by_token(token):
    result = ticket_service.get_ticket_by_token(token)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/bookings/<int:booking_id>/ticket")
def get_ticket_for_booking(booking_id):
    result = ticket_service.get_ticket_by_booking(booking_id)
    return jsonify(result), result.get("status", 200)


@ticket_bp.post("/tickets/<string:token>/verify")
def verify_ticket(token):
    data = request.get_json(silent=True) or {}
    result = ticket_service.verify_ticket(token, data)
    return jsonify(result), result.get("status", 200)
