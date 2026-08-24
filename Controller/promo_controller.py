# Controller/promo_controller.py
#
# PromoController — handles HTTP requests for promo code operations.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from Services.promo_service import PromoCodeService
from Controller.auth_guards import role_required

from api.schemas import (
    PromoValidateRequestSchema,
    PromoCreateRequestSchema,
    PromoUpdateRequestSchema,
    validate_payload,
)

promo_bp = Blueprint("promo_bp", __name__)
promo_service = PromoCodeService()


@promo_bp.post("/validate")
def validate_promo():
    """Validate a promo code and calculate discount for a subtotal."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(PromoValidateRequestSchema, data)
    if err_resp:
        return err_resp

    code = validated_data.get("code")
    amount = float(validated_data.get("amount", 0.0) or 0.0)

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
    except Exception:
        pass

    result = promo_service.validate_and_calculate_discount(
        code=code, user_id=user_id, order_subtotal=amount
    )
    return jsonify(result), result.get("status", 200)


@promo_bp.post("")
@jwt_required()
@role_required("admin")
def create_promo():
    """Create a new promo code (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(PromoCreateRequestSchema, data)
    if err_resp:
        return err_resp
    result = promo_service.create_promo(validated_data)
    return jsonify(result), result.get("status", 200)


@promo_bp.get("")
@jwt_required()
@role_required("admin")
def list_promos():
    """List all promo codes (Admin only)."""
    result = promo_service.get_all_promos()
    return jsonify(result), result.get("status", 200)


@promo_bp.get("/<int:promo_id>")
@jwt_required()
@role_required("admin")
def get_promo(promo_id):
    """Get a single promo code by id (Admin only)."""
    result = promo_service.get_promo_by_id(promo_id)
    return jsonify(result), result.get("status", 200)


@promo_bp.put("/<int:promo_id>")
@jwt_required()
@role_required("admin")
def update_promo(promo_id):
    """Update a promo code (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(PromoUpdateRequestSchema, data, partial=True)
    if err_resp:
        return err_resp
    result = promo_service.update_promo(promo_id, validated_data)
    return jsonify(result), result.get("status", 200)


@promo_bp.delete("/<int:promo_id>")
@jwt_required()
@role_required("admin")
def delete_promo(promo_id):
    """Delete a promo code (Admin only)."""
    result = promo_service.delete_promo(promo_id)
    return jsonify(result), result.get("status", 200)
