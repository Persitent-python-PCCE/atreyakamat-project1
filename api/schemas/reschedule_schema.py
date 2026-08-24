# api/schemas/reschedule_schema.py
#
# Marshmallow schemas for Event Rescheduling endpoints.

from marshmallow import Schema, fields, validate


class EventRescheduleRequestSchema(Schema):
    new_event_date = fields.String(required=True, validate=validate.Length(min=8, max=30))
    new_start_time = fields.String(required=True, validate=validate.Length(min=4, max=20))
    new_end_time = fields.String(required=False, allow_none=True)
    reason = fields.String(required=False, allow_none=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class EventRescheduleResponseSchema(Schema):
    id = fields.Integer()
    event_id = fields.Integer()
    admin_id = fields.Integer()
    old_event_date = fields.String()
    new_event_date = fields.String()
    old_start_time = fields.String()
    new_start_time = fields.String()
    old_end_time = fields.String(allow_none=True)
    new_end_time = fields.String(allow_none=True)
    reason = fields.String(allow_none=True)
    rescheduled_at = fields.DateTime(allow_none=True)
