# Controller/ticket_controller.py
#
# TicketController — handles HTTP requests for ticket retrieval and verification.
#
# Flow:
#     HTTP Request -> TicketController -> TicketService -> TicketDAO / TicketVerificationDAO -> MySQL

from flask import Blueprint, request, jsonify
from Services.ticket_service import TicketService

ticket_bp = Blueprint("ticket_bp", __name__)
ticket_service = TicketService()


@ticket_bp.get("/tickets/<string:token>")
def get_ticket_by_token(token):
    """Get ticket by unique ticket token."""
    result = ticket_service.get_ticket_by_token(token)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/bookings/<int:booking_id>/ticket")
def get_ticket_for_booking(booking_id):
    """Get ticket associated with a specific booking."""
    result = ticket_service.get_ticket_by_booking(booking_id)
    return jsonify(result), result.get("status", 200)


@ticket_bp.post("/tickets/<string:token>/verify")
def verify_ticket(token):
    """Record a ticket verification attempt."""
    data = request.get_json(silent=True) or {}
    result = ticket_service.verify_ticket(token, data)
    return jsonify(result), result.get("status", 200)
