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
    ("api.user_routes:user_bp", "/api/users"),
    ("api.category_routes:category_bp", "/api/categories"),
    ("api.venue_routes:venue_bp", "/api/venues"),
    ("api.event_routes:event_bp", "/api/events"),
    ("api.seat_routes:seat_bp", "/api"),
    ("api.booking_routes:booking_bp", "/api"),
    ("api.ticket_routes:ticket_bp", "/api"),
    ("api.notification_routes:notification_bp", "/api"),
    ("api.promo_routes:promo_bp", "/api/promos"),
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
