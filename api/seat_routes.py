# api/seat_routes.py
#
# Backward-compatibility alias for Controller.seat_controller.
# All seat controller logic lives in Controller/seat_controller.py.

from Controller.seat_controller import seat_bp, seat_service

__all__ = ["seat_bp", "seat_service"]
