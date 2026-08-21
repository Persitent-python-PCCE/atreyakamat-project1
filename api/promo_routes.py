# api/promo_routes.py
#
# CONTROLLER for promo codes.
#
#   POST   /api/promos
#   GET    /api/promos
#   GET    /api/promos/<id>
#   PUT    /api/promos/<id>
#   DELETE /api/promos/<id>

from flask import Blueprint, request, jsonify

from Services import PromoCodeService

promo_bp = Blueprint("promo_bp", __name__)
promo_service = PromoCodeService()


@promo_bp.post("")
def create_promo():
    data = request.get_json(silent=True) or {}
    result = promo_service.create_promo(data)
    return jsonify(result), result.get("status", 200)


@promo_bp.get("")
def list_promos():
    result = promo_service.get_all_promos()
    return jsonify(result), result.get("status", 200)


@promo_bp.get("/<int:promo_id>")
def get_promo(promo_id):
    result = promo_service.get_promo_by_id(promo_id)
    return jsonify(result), result.get("status", 200)


@promo_bp.put("/<int:promo_id>")
def update_promo(promo_id):
    data = request.get_json(silent=True) or {}
    result = promo_service.update_promo(promo_id, data)
    return jsonify(result), result.get("status", 200)


@promo_bp.delete("/<int:promo_id>")
def delete_promo(promo_id):
    result = promo_service.delete_promo(promo_id)
    return jsonify(result), result.get("status", 200)
