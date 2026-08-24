# api/schemas/common_schema.py
#
# Common Marshmallow validation utilities and response helpers for SeatMeUp.

from marshmallow import Schema, ValidationError, fields
from flask import jsonify


def validate_payload(schema_or_cls, data, partial=False):
    """Validate a request dictionary with a Marshmallow schema.

    Returns:
        tuple: (validated_dict, None) on success, or
               (None, (Flask JSON Response, 400)) on validation error.
    """
    schema = schema_or_cls() if isinstance(schema_or_cls, type) else schema_or_cls
    if data is None:
        data = {}
    try:
        validated = schema.load(data, partial=partial)
        return validated, None
    except ValidationError as err:
        return None, (
            jsonify({
                "success": False,
                "message": "Validation failed",
                "data": err.messages,
            }),
            400,
        )
