# api/booking_routes.py
#
# Backward-compatibility alias for Controller.booking_controller.
# All booking controller logic lives in Controller/booking_controller.py.

from Controller.booking_controller import booking_bp, booking_service

__all__ = ["booking_bp", "booking_service"]
