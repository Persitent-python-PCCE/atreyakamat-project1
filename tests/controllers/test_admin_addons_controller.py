# tests/controllers/test_admin_addons_controller.py
#
# Controller tests for Admin Add-ons CRUD routes (/admin/addons*).
# Verifies admin web access, creation, update, toggle active status, and deletion.

import re
import pytest
from models.event_addon import EventAddon


def extract_csrf_token(client, path="/admin/addons"):
    res = client.get(path)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if not match:
        match = re.search(r'value="([^"]+)"\s+name="csrf_token"', html)
    assert match is not None, f"Could not find CSRF token on page {path}"
    return match.group(1)


@pytest.mark.controller
class TestAdminAddonsController:
    def test_admin_addons_list_view(self, client, admin_token, event):
        """Admin can access GET /admin/addons and view add-ons list."""
        client.set_cookie("access_token_cookie", admin_token)
        res = client.get("/admin/addons")
        assert res.status_code == 200
        assert b"Event Add-ons" in res.data

    def test_admin_addons_customer_forbidden(self, client, customer_token):
        """Customer is blocked with 403 when accessing /admin/addons."""
        client.set_cookie("access_token_cookie", customer_token)
        res = client.get("/admin/addons")
        assert res.status_code == 403

    def test_admin_create_addon_post(self, client, admin_token, event, db_session):
        """Admin can create a new add-on via POST /admin/addons/create."""
        client.set_cookie("access_token_cookie", admin_token)
        token = extract_csrf_token(client, "/admin/addons")

        payload = {
            "csrf_token": token,
            "event_id": str(event.id),
            "name": "VIP Beverage Package",
            "price": "350.00",
            "available_quantity": "50",
            "description": "Unlimited drinks during the show",
            "is_active": "1",
        }
        res = client.post("/admin/addons/create", data=payload, follow_redirects=True)
        assert res.status_code == 200
        assert b"VIP Beverage Package" in res.data

        addon = EventAddon.query.filter_by(name="VIP Beverage Package").first()
        assert addon is not None
        assert float(addon.price) == 350.00
        assert addon.available_quantity == 50

    def test_admin_edit_addon_post(self, client, admin_token, event, db_session):
        """Admin can update an existing add-on via POST /admin/addons/<id>/edit."""
        client.set_cookie("access_token_cookie", admin_token)
        addon = EventAddon(
            event_id=event.id,
            name="Old Addon",
            price=100.00,
            available_quantity=20,
            is_active=True,
        )
        db_session.add(addon)
        db_session.commit()

        token = extract_csrf_token(client, "/admin/addons")
        edit_payload = {
            "csrf_token": token,
            "name": "Updated Addon Name",
            "price": "175.00",
            "available_quantity": "40",
            "description": "Updated Description",
            "is_active": "1",
        }
        res = client.post(f"/admin/addons/{addon.id}/edit", data=edit_payload, follow_redirects=True)
        assert res.status_code == 200
        assert b"Updated Addon Name" in res.data

        updated = EventAddon.query.get(addon.id)
        assert updated.name == "Updated Addon Name"
        assert float(updated.price) == 175.00
        assert updated.available_quantity == 40

    def test_admin_toggle_addon_post(self, client, admin_token, event, db_session):
        """Admin can toggle addon active state via POST /admin/addons/<id>/toggle."""
        client.set_cookie("access_token_cookie", admin_token)
        addon = EventAddon(
            event_id=event.id,
            name="Toggleable Addon",
            price=50.00,
            available_quantity=10,
            is_active=True,
        )
        db_session.add(addon)
        db_session.commit()

        token = extract_csrf_token(client, "/admin/addons")

        # Toggle to inactive
        res = client.post(f"/admin/addons/{addon.id}/toggle", data={"csrf_token": token}, follow_redirects=True)
        assert res.status_code == 200
        assert EventAddon.query.get(addon.id).is_active is False

        # Toggle back to active
        res2 = client.post(f"/admin/addons/{addon.id}/toggle", data={"csrf_token": token}, follow_redirects=True)
        assert res2.status_code == 200
        assert EventAddon.query.get(addon.id).is_active is True

    def test_admin_delete_addon_post(self, client, admin_token, event, db_session):
        """Admin can delete an add-on via POST /admin/addons/<id>/delete."""
        client.set_cookie("access_token_cookie", admin_token)
        addon = EventAddon(
            event_id=event.id,
            name="Addon to Delete",
            price=25.00,
            available_quantity=5,
            is_active=True,
        )
        db_session.add(addon)
        db_session.commit()

        token = extract_csrf_token(client, "/admin/addons")
        res = client.post(f"/admin/addons/{addon.id}/delete", data={"csrf_token": token}, follow_redirects=True)
        assert res.status_code == 200
        assert EventAddon.query.get(addon.id) is None
