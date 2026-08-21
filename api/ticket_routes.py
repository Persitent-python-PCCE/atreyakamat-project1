# api/ticket_routes.py
#
# Backward-compatibility alias for Controller.ticket_controller.
# All ticket controller logic lives in Controller/ticket_controller.py.

from Controller.ticket_controller import ticket_bp, ticket_service

__all__ = ["ticket_bp", "ticket_service"]
