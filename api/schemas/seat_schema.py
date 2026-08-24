# api/schemas/seat_schema.py
#
# Marshmallow schemas for Seat endpoints.

from marshmallow import Schema, fields, validate


class SeatCreateRequestSchema(Schema):
    venue_id = fields.Integer(required=False, validate=validate.Range(min=1))
    seat_number = fields.String(required=True, validate=validate.Length(min=1, max=20))
    section_name = fields.String(required=False, validate=validate.Length(min=1, max=50))
    seat_type = fields.String(required=False, validate=validate.OneOf(["standard", "vip", "accessible"]))
    price = fields.Float(required=False, validate=validate.Range(min=0.0))
    is_active = fields.Boolean(required=False)


class SeatResponseSchema(Schema):
    id = fields.Integer()
    venue_id = fields.Integer()
    seat_number = fields.String()
    section_name = fields.String()
    seat_type = fields.String()
    price = fields.Float()
    is_active = fields.Boolean()
    created_at = fields.DateTime(allow_none=True)
