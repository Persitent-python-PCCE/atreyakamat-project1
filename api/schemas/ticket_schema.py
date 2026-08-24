# api/schemas/ticket_schema.py
#
# Marshmallow schemas for Ticket and Verification endpoints.

from marshmallow import Schema, fields


class TicketVerifyRequestSchema(Schema):
    ticket_token = fields.String(required=False)
    mark_as_used = fields.Boolean(required=False)


class TicketResponseSchema(Schema):
    id = fields.Integer()
    booking_id = fields.Integer()
    ticket_token = fields.String()
    ticket_status = fields.String()
    qr_data = fields.String(allow_none=True)
    issued_at = fields.DateTime(allow_none=True)
    used_at = fields.DateTime(allow_none=True)
    expired_at = fields.DateTime(allow_none=True)


class TicketVerificationResponseSchema(Schema):
    id = fields.Integer()
    ticket_id = fields.Integer()
    verification_status = fields.String()
    verified_at = fields.DateTime(allow_none=True)
