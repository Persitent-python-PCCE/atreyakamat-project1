# api/category_routes.py
#
# Backward-compatibility alias for Controller.category_controller.
# All category controller logic lives in Controller/category_controller.py.

from Controller.category_controller import category_bp, category_service

__all__ = ["category_bp", "category_service"]
