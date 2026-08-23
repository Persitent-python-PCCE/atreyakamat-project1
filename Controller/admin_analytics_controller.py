# Controller/admin_analytics_controller.py
#
# AdminAnalyticsController — REST API endpoints for Admin Analytics.
#
# Routes:
#   GET /api/admin/analytics

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from Services.analytics_service import AnalyticsService

admin_analytics_bp = Blueprint("admin_analytics_bp", __name__)
analytics_service = AnalyticsService()


@admin_analytics_bp.get("/analytics")
@jwt_required()
def get_admin_analytics():
    """Retrieve platform analytics metrics and breakdowns (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({
            "success": False,
            "message": "Admin access required",
        }), 403

    days_param = request.args.get("days")
    days = int(days_param) if days_param and days_param.isdigit() else None

    result = analytics_service.get_full_analytics(days=days)
    return jsonify(result), result.get("status", 200)


@admin_analytics_bp.post("/events/<int:event_id>/reschedule")
@jwt_required()
def api_reschedule_event(event_id):
    """Reschedule an existing event with admin password confirmation (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({
            "success": False,
            "message": "Admin access required",
        }), 403

    from flask_jwt_extended import get_jwt_identity
    from Services.event_reschedule_service import EventRescheduleService
    reschedule_service = EventRescheduleService()

    admin_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    new_event_date = data.get("new_event_date")
    new_start_time = data.get("new_start_time")
    new_end_time = data.get("new_end_time")
    reason = data.get("reason")
    password = data.get("password")

    if not password:
        return jsonify({
            "success": False,
            "message": "Admin password confirmation is required.",
        }), 400

    result = reschedule_service.reschedule_event(
        event_id=event_id,
        admin_id=admin_id,
        password=password,
        new_event_date=new_event_date,
        new_start_time=new_start_time,
        new_end_time=new_end_time,
        reason=reason,
    )
    return jsonify(result), result.get("status", 200)


@admin_analytics_bp.get("/events/<int:event_id>/reschedule-history")
@jwt_required()
def api_get_reschedule_history(event_id):
    """Retrieve audit history for an event (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({
            "success": False,
            "message": "Admin access required",
        }), 403

    from Services.event_reschedule_service import EventRescheduleService
    reschedule_service = EventRescheduleService()

    result = reschedule_service.get_reschedule_history(event_id)
    return jsonify(result), result.get("status", 200)


@admin_analytics_bp.post("/events")
@jwt_required()
def api_admin_create_event():
    """Create a new event via /api/admin/events (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({"success": False, "message": "Admin access required"}), 403

    from flask_jwt_extended import get_jwt_identity
    from Services.event_service import EventService
    event_service = EventService()

    data = request.get_json(silent=True) or {}
    if "created_by" not in data:
        data["created_by"] = int(get_jwt_identity())

    result = event_service.create_event(data)
    return jsonify(result), result.get("status", 200)


@admin_analytics_bp.put("/events/<int:event_id>")
@jwt_required()
def api_admin_update_event(event_id):
    """Update an event via /api/admin/events/<id> (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({"success": False, "message": "Admin access required"}), 403

    from Services.event_service import EventService
    event_service = EventService()

    data = request.get_json(silent=True) or {}
    result = event_service.update_event(event_id, data)
    return jsonify(result), result.get("status", 200)


@admin_analytics_bp.delete("/events/<int:event_id>")
@jwt_required()
def api_admin_delete_event(event_id):
    """Delete an event via /api/admin/events/<id> (Admin only)."""
    jwt_claims = get_jwt()
    if jwt_claims.get("role") != "admin":
        return jsonify({"success": False, "message": "Admin access required"}), 403

    from Services.event_service import EventService
    event_service = EventService()

    result = event_service.delete_event(event_id)
    return jsonify(result), result.get("status", 200)
