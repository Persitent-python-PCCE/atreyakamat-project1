# api/schemas/category_schema.py
#
# Marshmallow schemas for Category endpoints.

from marshmallow import Schema, fields, validate


class CategoryCreateRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, allow_none=True)


class CategoryUpdateRequestSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, allow_none=True)


class CategoryResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
