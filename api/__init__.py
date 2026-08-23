# api/ package
#
# This package holds the REST API (Controller) layer for SeatMeUp.
# It is built with Flask Blueprints — one file per resource.

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
    ("Controller.admin_analytics_controller:admin_analytics_bp", "/api/admin"),
]


def register_blueprints(app, csrf=None):
    """Register every API blueprint on the given Flask app and exempt REST APIs from CSRF."""
    from importlib import import_module

    for dotted_path, url_prefix in ALL_BLUEPRINT_SPECS:
        module_name, attr_name = dotted_path.rsplit(":", 1)
        module = import_module(module_name)
        blueprint = getattr(module, attr_name)

        # Exempt REST API blueprints from HTML form CSRF token requirement
        # (web_auth_bp remains protected by CSRF)
        if csrf is not None and attr_name != "web_auth_bp":
            csrf.exempt(blueprint)

        app.register_blueprint(blueprint, url_prefix=url_prefix)


__all__ = [
    "ok",
    "err",
    "ALL_BLUEPRINT_SPECS",
    "register_blueprints",
]
