# api/promo_routes.py
#
# Backward-compatibility alias for Controller.promo_controller.
# All promo controller logic lives in Controller/promo_controller.py.

from Controller.promo_controller import promo_bp, promo_service

__all__ = ["promo_bp", "promo_service"]
