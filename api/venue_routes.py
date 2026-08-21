# api/venue_routes.py
#
# Backward-compatibility alias for Controller.venue_controller.
# All venue controller logic lives in Controller/venue_controller.py.

from Controller.venue_controller import venue_bp, venue_service

__all__ = ["venue_bp", "venue_service"]
