# api/schemas/auth_schema.py
#
# Marshmallow schemas for Authentication endpoints (Register & Login).

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class RegisterRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=150))
    password = fields.String(required=True, validate=validate.Length(min=4, max=128))
    confirm_password = fields.String(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=20))
    role = fields.String(required=False, validate=validate.OneOf(["customer", "admin"]))

    @validates_schema
    def validate_password_confirmation(self, data, **kwargs):
        if "confirm_password" in data and data.get("confirm_password"):
            if data.get("password") != data.get("confirm_password"):
                raise ValidationError({"confirm_password": ["Passwords do not match."]})


class LoginRequestSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(min=1, max=150))
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))
