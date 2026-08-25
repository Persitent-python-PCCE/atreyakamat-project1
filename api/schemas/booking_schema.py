# api/schemas/booking_schema.py
#
# Marshmallow schemas for Booking and Checkout endpoints.

from marshmallow import Schema, fields, validate


class CheckoutPreviewRequestSchema(Schema):
    event_id = fields.Integer(required=True, validate=validate.Range(min=1))
    promo_code = fields.String(required=False, allow_none=True)
    selected_addons = fields.Dict(required=False)
    quantity = fields.Integer(required=False, allow_none=True, validate=validate.Range(min=1))


class CheckoutConfirmRequestSchema(Schema):
    event_id = fields.Integer(required=True, validate=validate.Range(min=1))
    promo_code = fields.String(required=False, allow_none=True)
    selected_addons = fields.Dict(required=False)
    quantity = fields.Integer(required=False, allow_none=True, validate=validate.Range(min=1))
    idempotency_key = fields.String(required=False, allow_none=True)


class BookingResponseSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    event_id = fields.Integer()
    booking_reference = fields.String()
    total_amount = fields.Float()
    discount_amount = fields.Float()
    cashback_amount = fields.Float()
    idempotency_key = fields.String(allow_none=True)
    status = fields.String()
    booked_at = fields.DateTime(allow_none=True)
    cancelled_at = fields.DateTime(allow_none=True)
