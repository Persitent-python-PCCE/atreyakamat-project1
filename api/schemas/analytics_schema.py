# api/schemas/analytics_schema.py
#
# Marshmallow schemas for Admin Analytics endpoints.

from marshmallow import Schema, fields


class AnalyticsSummaryResponseSchema(Schema):
    total_events = fields.Integer()
    active_events = fields.Integer()
    total_bookings = fields.Integer()
    cancelled_bookings = fields.Integer()
    total_revenue = fields.Float()
    cashback_given = fields.Float()
    total_tickets_sold = fields.Integer()
    average_booking_value = fields.Float()
