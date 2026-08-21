# Controller/promo_controller.py
#
# PromoController — handles HTTP requests for promo code operations.
#
# Flow:
#     HTTP Request -> PromoController -> PromoCodeService -> PromoCodeDAO -> MySQL

from flask import Blueprint, request, jsonify
from Services.promo_service import PromoCodeService

promo_bp = Blueprint("promo_bp", __name__)
promo_service = PromoCodeService()


@promo_bp.post("")
def create_promo():
    """Create a new promo code."""
    data = request.get_json(silent=True) or {}
    result = promo_service.create_promo(data)
    return jsonify(result), result.get("status", 200)


@promo_bp.get("")
def list_promos():
    """List all promo codes."""
    result = promo_service.get_all_promos()
    return jsonify(result), result.get("status", 200)


@promo_bp.get("/<int:promo_id>")
def get_promo(promo_id):
    """Get a single promo code by id."""
    result = promo_service.get_promo_by_id(promo_id)
    return jsonify(result), result.get("status", 200)


@promo_bp.put("/<int:promo_id>")
def update_promo(promo_id):
    """Update a promo code."""
    data = request.get_json(silent=True) or {}
    result = promo_service.update_promo(promo_id, data)
    return jsonify(result), result.get("status", 200)


@promo_bp.delete("/<int:promo_id>")
def delete_promo(promo_id):
    """Delete a promo code."""
    result = promo_service.delete_promo(promo_id)
    return jsonify(result), result.get("status", 200)
