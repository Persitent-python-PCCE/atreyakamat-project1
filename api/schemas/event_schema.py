# api/schemas/event_schema.py
#
# Marshmallow schemas for Event endpoints.

from marshmallow import Schema, fields, validate


class EventCreateRequestSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    category_id = fields.Integer(required=True, validate=validate.Range(min=1))
    venue_id = fields.Integer(required=True, validate=validate.Range(min=1))
    event_date = fields.String(required=True, validate=validate.Length(min=8, max=30))
    start_time = fields.String(required=True, validate=validate.Length(min=4, max=20))
    end_time = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    poster = fields.String(required=False, allow_none=True)
    booking_open = fields.Boolean(required=False)
    requires_seats = fields.Boolean(required=False)
    base_price = fields.Float(required=False, validate=validate.Range(min=0.0))
    status = fields.String(required=False, validate=validate.OneOf(["published", "draft", "cancelled", "completed"]))
    created_by = fields.Integer(required=False)


class EventUpdateRequestSchema(Schema):
    title = fields.String(required=False, validate=validate.Length(min=1, max=200))
    category_id = fields.Integer(required=False, validate=validate.Range(min=1))
    venue_id = fields.Integer(required=False, validate=validate.Range(min=1))
    event_date = fields.String(required=False, validate=validate.Length(min=8, max=30))
    start_time = fields.String(required=False, validate=validate.Length(min=4, max=20))
    end_time = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    poster = fields.String(required=False, allow_none=True)
    booking_open = fields.Boolean(required=False)
    requires_seats = fields.Boolean(required=False)
    base_price = fields.Float(required=False, validate=validate.Range(min=0.0))
    status = fields.String(required=False, validate=validate.OneOf(["published", "draft", "cancelled", "completed"]))


class EventResponseSchema(Schema):
    id = fields.Integer()
    category_id = fields.Integer()
    category_name = fields.String(allow_none=True)
    venue_id = fields.Integer()
    venue_name = fields.String(allow_none=True)
    venue_city = fields.String(allow_none=True)
    created_by = fields.Integer()
    title = fields.String()
    description = fields.String(allow_none=True)
    event_date = fields.String()
    start_time = fields.String()
    end_time = fields.String(allow_none=True)
    poster = fields.String(allow_none=True)
    booking_open = fields.Boolean()
    status = fields.String()
    requires_seats = fields.Boolean()
    base_price = fields.Float()
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
