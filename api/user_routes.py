# api/user_routes.py
#
# Backward-compatibility alias for Controller.user_controller.
# All user controller logic lives in Controller/user_controller.py.

from Controller.user_controller import user_bp, user_service

__all__ = ["user_bp", "user_service"]
