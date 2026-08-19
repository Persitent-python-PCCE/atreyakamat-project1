from flask import Blueprint, render_template

from Services.event_service import EventService


event_bp = Blueprint("event_bp", __name__)
event_service = EventService()


@event_bp.route("/events")
def list_events():
    events = event_service.get_upcoming_events()
    return render_template("events.html", events=events)


@event_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    event = event_service.get_event_by_id(event_id)
    return render_template("event_detail.html", event=event)
