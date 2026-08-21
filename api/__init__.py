# api/ package
#
# This package holds the REST API (Controller) layer for SeatMeUp.
# It is built with Flask Blueprints — one file per resource.
#
# Each blueprint file (e.g. user_routes.py) defines HTTP routes that:
#   - receive JSON via request.get_json()
#   - call the matching Service (which in turn calls the DAO)
#   - return a consistent JSON response:
#         {"success": ..., "message": ..., "data": ...}
#
# Why the blueprint imports are deferred into register_blueprints():
#   A Service module imports `from api.serializers import xxx_to_dict`.
#   Importing any submodule of `api` runs api/__init__.py first. If
#   api/__init__.py eagerly imported the blueprint modules at the top,
#   that would trigger the Service import, which would trigger api again
#   — a circular import. By deferring the blueprint imports until
#   register_blueprints() is actually called (inside create_app, AFTER the
#   app and `db` exist and the Service package is fully loaded), we break
#   the cycle cleanly. This matches the same pattern used in app.py.
#
# `api.serializers` is the only submodule that other packages (Services,
# tests) import directly. It is intentional that it has no dependencies on
# the blueprint modules.

from .serializers import ok, err  # noqa: F401  (re-exported for convenience)

# The map of (blueprint_import_path, url_prefix) is defined here so the
# registration logic stays in one place. Actual blueprint objects are
# imported lazily inside register_blueprints() to avoid circular imports.
ALL_BLUEPRINT_SPECS = [
    ("Controller.auth_controller:api_auth_bp", "/api/auth"),
    ("Controller.auth_controller:web_auth_bp", ""),
    ("Controller.user_controller:user_bp", "/api/users"),
    ("Controller.category_controller:category_bp", "/api/categories"),
    ("Controller.venue_controller:venue_bp", "/api/venues"),
    ("Controller.event_controller:event_bp", "/api/events"),
    ("Controller.seat_controller:seat_bp", "/api"),
    ("Controller.booking_controller:booking_bp", "/api"),
    ("Controller.ticket_controller:ticket_bp", "/api"),
    ("Controller.notification_controller:notification_bp", "/api"),
    ("Controller.promo_controller:promo_bp", "/api/promos"),
]


def register_blueprints(app):
    """Register every API blueprint on the given Flask app.

    app.py calls this once inside create_app(). Blueprint objects are
    imported HERE (lazily), after the app and `db` already exist, so that
    there is no chance of a circular import while modules are still loading.
    """
    from importlib import import_module

    for dotted_path, url_prefix in ALL_BLUEPRINT_SPECS:
        module_name, attr_name = dotted_path.rsplit(":", 1)
        module = import_module(module_name)
        blueprint = getattr(module, attr_name)
        app.register_blueprint(blueprint, url_prefix=url_prefix)


__all__ = [
    "ok",
    "err",
    "ALL_BLUEPRINT_SPECS",
    "register_blueprints",
]
