# api/schemas/promo_schema.py
#
# Marshmallow schemas for Promo Code endpoints.

from marshmallow import Schema, fields, validate


class PromoValidateRequestSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    amount = fields.Float(required=False, validate=validate.Range(min=0.0))


class PromoCreateRequestSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    description = fields.String(required=False, allow_none=True)
    discount_type = fields.String(required=True, validate=validate.OneOf(["percentage", "fixed"]))
    discount_value = fields.Float(required=True, validate=validate.Range(min=0.01))
    minimum_booking_amount = fields.Float(required=False, validate=validate.Range(min=0.0))
    max_uses = fields.Integer(required=False, validate=validate.Range(min=1))
    valid_from = fields.DateTime(required=False, allow_none=True)
    valid_until = fields.DateTime(required=False, allow_none=True)
    is_active = fields.Boolean(required=False)


class PromoUpdateRequestSchema(Schema):
    description = fields.String(required=False, allow_none=True)
    discount_type = fields.String(required=False, validate=validate.OneOf(["percentage", "fixed"]))
    discount_value = fields.Float(required=False, validate=validate.Range(min=0.01))
    minimum_booking_amount = fields.Float(required=False, validate=validate.Range(min=0.0))
    max_uses = fields.Integer(required=False, validate=validate.Range(min=1))
    valid_from = fields.DateTime(required=False, allow_none=True)
    valid_until = fields.DateTime(required=False, allow_none=True)
    is_active = fields.Boolean(required=False)


class PromoResponseSchema(Schema):
    id = fields.Integer()
    code = fields.String()
    description = fields.String(allow_none=True)
    discount_type = fields.String()
    discount_value = fields.Float()
    minimum_booking_amount = fields.Float()
    max_uses = fields.Integer()
    used_count = fields.Integer()
    valid_from = fields.DateTime(allow_none=True)
    valid_until = fields.DateTime(allow_none=True)
    is_active = fields.Boolean()
    created_at = fields.DateTime(allow_none=True)
