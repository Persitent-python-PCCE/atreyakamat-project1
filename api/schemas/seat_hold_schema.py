# api/schemas/seat_hold_schema.py
#
# Marshmallow schemas for SeatHold serialization.

from marshmallow import Schema, fields


class SeatHoldResponseSchema(Schema):
    id = fields.Integer()
    event_id = fields.Integer()
    seat_id = fields.Integer()
    user_id = fields.Integer()
    hold_token = fields.String()
    held_at = fields.DateTime(allow_none=True)
    expires_at = fields.DateTime(allow_none=True)
    status = fields.String()
