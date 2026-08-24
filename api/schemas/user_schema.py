# api/schemas/user_schema.py
#
# Marshmallow schemas for User management and serialization.

from marshmallow import Schema, fields, validate


class UserCreateRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=150))
    password = fields.String(required=True, validate=validate.Length(min=4, max=128))
    role = fields.String(required=False, validate=validate.OneOf(["customer", "admin"]))
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    id_document = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))


class UserUpdateRequestSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=False, validate=validate.Length(max=150))
    password = fields.String(required=False, validate=validate.Length(min=4, max=128))
    role = fields.String(required=False, validate=validate.OneOf(["customer", "admin"]))
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    id_document = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    is_active = fields.Boolean(required=False)


class UserResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.String()
    role = fields.String()
    phone = fields.String(allow_none=True)
    id_document = fields.String(allow_none=True)
    reward_balance = fields.Float(allow_none=True)
    is_active = fields.Boolean()
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
    # NOTE: password_hash is intentionally excluded from all User serialized outputs
