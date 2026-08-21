# api/notification_routes.py
#
# Backward-compatibility alias for Controller.notification_controller.
# All notification controller logic lives in Controller/notification_controller.py.

from Controller.notification_controller import notification_bp, notification_service

__all__ = ["notification_bp", "notification_service"]
