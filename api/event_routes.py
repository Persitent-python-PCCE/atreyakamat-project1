# api/event_routes.py
#
# Backward-compatibility alias for Controller.event_controller.
# All event controller logic lives in Controller/event_controller.py.

from Controller.event_controller import event_bp, event_service

__all__ = ["event_bp", "event_service"]
