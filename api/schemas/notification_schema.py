# api/schemas/notification_schema.py
#
# Marshmallow schemas for Notification endpoints.

from marshmallow import Schema, fields, validate


class NotificationCreateRequestSchema(Schema):
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    message = fields.String(required=True, validate=validate.Length(min=1))
    notification_type = fields.String(required=False, validate=validate.OneOf(["info", "warning", "success", "danger"]))


class NotificationResponseSchema(Schema):
    id = fields.Integer()
    user_id = fields.Integer()
    title = fields.String()
    message = fields.String()
    notification_type = fields.String()
    is_read = fields.Boolean()
    created_at = fields.DateTime(allow_none=True)
