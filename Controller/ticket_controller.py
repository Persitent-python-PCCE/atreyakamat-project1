# Controller/ticket_controller.py
#
# TicketController — handles HTTP REST API requests for tickets and verification scans.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from Services.ticket_service import TicketService

from api.schemas import TicketVerifyRequestSchema, validate_payload

ticket_bp = Blueprint("ticket_bp", __name__)
ticket_service = TicketService()


@ticket_bp.get("/tickets/<int:ticket_id>")
def get_ticket_by_id(ticket_id):
    """Get rich ticket details by numeric ticket ID."""
    ticket = ticket_service.ticket_dao.get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({"success": False, "message": "Ticket not found"}), 404
    result = ticket_service.get_ticket_details_by_token(ticket.ticket_token)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/tickets/<string:token>")
@ticket_bp.get("/tickets/token/<string:token>")
def get_ticket_by_token(token):
    """Get rich ticket details by unique ticket token."""
    result = ticket_service.get_ticket_details_by_token(token)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/bookings/<int:booking_id>/ticket")
def get_ticket_for_booking(booking_id):
    """Get ticket associated with a specific booking."""
    result = ticket_service.get_ticket_by_booking(booking_id)
    return jsonify(result), result.get("status", 200)


@ticket_bp.post("/tickets/<int:ticket_id>/verify")
def verify_ticket_by_id(ticket_id):
    """Verify and validate a ticket by numeric ID (marks as used on success)."""
    ticket = ticket_service.ticket_dao.get_ticket_by_id(ticket_id)
    if not ticket:
        return jsonify({"success": False, "message": "Ticket not found"}), 404
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(TicketVerifyRequestSchema, data, partial=True)
    if err_resp:
        return err_resp
    mark_used = validated_data.get("mark_as_used", True) if validated_data.get("mark_as_used") is not None else True
    result = ticket_service.validate_and_verify_ticket(ticket.ticket_token, mark_as_used=mark_used)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/tickets/verify/<string:token>")
@ticket_bp.post("/tickets/verify")
@ticket_bp.post("/tickets/<string:token>/verify")
def verify_ticket(token=None):
    """Verify and validate a ticket token (marks as used on success)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(TicketVerifyRequestSchema, data, partial=True)
    if err_resp:
        return err_resp

    token_to_verify = token or validated_data.get("ticket_token")
    mark_used = validated_data.get("mark_as_used", True) if validated_data.get("mark_as_used") is not None else True

    if not token_to_verify:
        return jsonify({"success": False, "message": "ticket_token is required"}), 400

    result = ticket_service.validate_and_verify_ticket(token_to_verify, mark_as_used=mark_used)
    return jsonify(result), result.get("status", 200)


@ticket_bp.get("/tickets/<int:ticket_id>/verifications")
def get_ticket_verifications(ticket_id):
    """Get verification scan history for a ticket."""
    result = ticket_service.get_ticket_verifications(ticket_id)
    return jsonify(result), result.get("status", 200)
