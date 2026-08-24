# api/schemas/venue_schema.py
#
# Marshmallow schemas for Venue endpoints.

from marshmallow import Schema, fields, validate


class VenueCreateRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    address = fields.String(required=True, validate=validate.Length(min=1, max=255))
    city = fields.String(required=True, validate=validate.Length(min=1, max=100))
    state = fields.String(required=True, validate=validate.Length(min=1, max=100))
    capacity = fields.Integer(required=True, validate=validate.Range(min=1))
    venue_type = fields.String(required=False, validate=validate.OneOf(["seated", "general"]))


class VenueUpdateRequestSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=150))
    address = fields.String(required=False, validate=validate.Length(min=1, max=255))
    city = fields.String(required=False, validate=validate.Length(min=1, max=100))
    state = fields.String(required=False, validate=validate.Length(min=1, max=100))
    capacity = fields.Integer(required=False, validate=validate.Range(min=1))
    venue_type = fields.String(required=False, validate=validate.OneOf(["seated", "general"]))


class VenueResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    address = fields.String()
    city = fields.String()
    state = fields.String()
    capacity = fields.Integer()
    venue_type = fields.String()
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
