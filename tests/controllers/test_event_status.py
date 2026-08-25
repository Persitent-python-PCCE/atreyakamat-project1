# tests/controllers/test_event_status.py
#
# Dedicated test suite for the Event status system ('published' / 'unpublished' ONLY).
# WHY: Guarantees that Event status is strictly binary (published or unpublished),
# correctly governs customer visibility, search filtering, seat hold guards,
# and checkout protection, while rejecting legacy/custom statuses across all layers.

import pytest
from datetime import date, timedelta, time
from models.user import User
from models.category import Category
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from Services.event_service import EventService
from Services.seat_service import SeatService
from Services.booking_service import BookingService


@pytest.mark.controller
@pytest.mark.unit
class TestEventStatusSystem:
    @pytest.fixture
    def test_env(self, db_session):
        admin = User(name="Status Admin", email="statusadmin@seatmeup.com", password_hash="pw", role="admin")
        customer = User(name="Status Customer", email="statuscust@example.com", password_hash="pw", role="customer")
        cat = Category(name="Status Category")
        ven = Venue(name="Status Hall", address="100 Test Blvd", venue_type="seated", capacity=10)
        db_session.add_all([admin, customer, cat, ven])
        db_session.commit()

        # Add 2 seats to venue
        s1 = Seat(venue_id=ven.id, seat_number="A1", section_name="Orchestra", price=100.00, is_active=True)
        s2 = Seat(venue_id=ven.id, seat_number="A2", section_name="Orchestra", price=100.00, is_active=True)
        db_session.add_all([s1, s2])
        db_session.commit()

        return {
            "admin": admin,
            "customer": customer,
            "category": cat,
            "venue": ven,
            "seat1": s1,
            "seat2": s2,
        }

    # 1. New event defaults to unpublished
    def test_new_event_defaults_to_unpublished(self, test_env, db_session):
        svc = EventService()
        res = svc.create_event({
            "title": "Default Status Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "base_price": 50.00,
        })
        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["status"] == "unpublished"

        ev_db = db_session.get(Event, res["data"]["id"])
        assert ev_db.status == "unpublished"

    # 2. Admin can publish an event
    def test_admin_can_publish_an_event(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Publishable Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })
        event_id = create_res["data"]["id"]

        pub_res = svc.update_event(event_id, {"status": "published"})
        assert pub_res["success"] is True
        assert pub_res["data"]["status"] == "published"

    # 3. Admin can unpublish an event
    def test_admin_can_unpublish_an_event(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Unpublishable Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "published",
        })
        event_id = create_res["data"]["id"]

        unpub_res = svc.update_event(event_id, {"status": "unpublished"})
        assert unpub_res["success"] is True
        assert unpub_res["data"]["status"] == "unpublished"

    # 4-7. Invalid statuses rejected: draft, cancelled, completed, arbitrary
    @pytest.mark.parametrize("invalid_status", ["draft", "cancelled", "completed", "archived", "pending", "xyz"])
    def test_invalid_statuses_rejected_on_create_and_update(self, test_env, invalid_status):
        svc = EventService()
        # Rejected on create
        res_create = svc.create_event({
            "title": f"Invalid {invalid_status} Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": invalid_status,
        })
        assert res_create["success"] is False
        assert res_create["status"] == 400
        assert "Invalid event status" in res_create["message"]

        # Rejected on update
        valid_ev = svc.create_event({
            "title": "Valid Event For Bad Update",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "published",
        })
        ev_id = valid_ev["data"]["id"]

        res_update = svc.update_event(ev_id, {"status": invalid_status})
        assert res_update["success"] is False
        assert res_update["status"] == 400
        assert "Invalid event status" in res_update["message"]

    # 8. Unpublished event hidden from public event list
    def test_unpublished_event_hidden_from_public_event_list(self, test_env):
        svc = EventService()
        svc.create_event({
            "title": "Secret Unpublished Concert",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })
        svc.create_event({
            "title": "Public Live Show",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "published",
        })

        public_res = svc.get_all_events(include_unpublished=False)
        titles = [e["title"] for e in public_res["data"]]
        assert "Public Live Show" in titles
        assert "Secret Unpublished Concert" not in titles

    # 9. Unpublished event hidden from search
    def test_unpublished_event_hidden_from_search(self, test_env):
        svc = EventService()
        svc.create_event({
            "title": "Unique Unpublished Keyword",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })

        search_res = svc.search_events("Unique Unpublished Keyword")
        assert len(search_res["data"]) == 0

    # 10. Unpublished event hidden from category listing
    def test_unpublished_event_hidden_from_category_listing(self, test_env):
        svc = EventService()
        svc.create_event({
            "title": "Category Secret Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })

        cat_res = svc.get_events_by_category(test_env["category"].id)
        titles = [e["title"] for e in cat_res["data"]]
        assert "Category Secret Event" not in titles

    # 11. Unpublished event hidden from upcoming events
    def test_unpublished_event_hidden_from_upcoming_events(self, test_env):
        svc = EventService()
        svc.create_event({
            "title": "Future Unpublished Gala",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })

        upcoming_res = svc.get_upcoming_events()
        titles = [e["title"] for e in upcoming_res["data"]]
        assert "Future Unpublished Gala" not in titles

    # 12. Customer cannot access unpublished event booking / details directly
    def test_customer_cannot_access_unpublished_event_direct(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Direct Link Hidden Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })
        event_id = create_res["data"]["id"]

        # Public lookup returns 404
        direct_res = svc.get_event_by_id(event_id, include_unpublished=False)
        assert direct_res["success"] is False
        assert direct_res["status"] == 404

    # 13. Customer cannot hold seats for unpublished event
    def test_customer_cannot_hold_seats_for_unpublished_event(self, test_env):
        svc = EventService()
        seat_svc = SeatService()
        create_res = svc.create_event({
            "title": "Unpublished Seat Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
            "requires_seats": True,
        })
        event_id = create_res["data"]["id"]

        hold_res = seat_svc.hold_seat(
            event_id=event_id,
            seat_id=test_env["seat1"].id,
            user_id=test_env["customer"].id,
        )
        assert hold_res["success"] is False
        assert hold_res["status"] == 400
        assert "not available for booking" in hold_res["message"]

    # 14. Customer cannot checkout unpublished event
    def test_customer_cannot_checkout_unpublished_event(self, test_env):
        svc = EventService()
        bk_svc = BookingService()
        create_res = svc.create_event({
            "title": "Unpublished Checkout Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
            "requires_seats": False,
        })
        event_id = create_res["data"]["id"]

        preview_res = bk_svc.get_checkout_preview(
            user_id=test_env["customer"].id,
            event_id=event_id,
            quantity=1,
        )
        assert preview_res["success"] is False
        assert preview_res["status"] == 400

        confirm_res = bk_svc.confirm_booking(
            user_id=test_env["customer"].id,
            event_id=event_id,
            quantity=1,
        )
        assert confirm_res["success"] is False
        assert confirm_res["status"] == 400

    # 15. Admin can still view unpublished event
    def test_admin_can_view_unpublished_event(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Admin Inspection Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "unpublished",
        })
        event_id = create_res["data"]["id"]

        admin_res = svc.get_event_by_id(event_id, include_unpublished=True)
        assert admin_res["success"] is True
        assert admin_res["data"]["title"] == "Admin Inspection Event"

        admin_all = svc.get_all_events(include_unpublished=True)
        assert any(e["id"] == event_id for e in admin_all["data"])

    # 16. Published event appears publicly
    def test_published_event_appears_publicly(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Promoted Grand Symphony",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "published",
        })
        event_id = create_res["data"]["id"]

        pub_get = svc.get_event_by_id(event_id, include_unpublished=False)
        assert pub_get["success"] is True
        assert pub_get["data"]["status"] == "published"

    # 17. Published event remains bookable when booking_open is true
    def test_published_event_remains_bookable(self, test_env):
        svc = EventService()
        seat_svc = SeatService()
        bk_svc = BookingService()

        create_res = svc.create_event({
            "title": "Bookable Symphony",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "base_price": 100.00,
            "status": "published",
            "booking_open": True,
            "requires_seats": True,
        })
        event_id = create_res["data"]["id"]

        hold_res = seat_svc.hold_seat(
            event_id=event_id,
            seat_id=test_env["seat1"].id,
            user_id=test_env["customer"].id,
        )
        assert hold_res["success"] is True
        assert hold_res["status"] == 201

        preview_res = bk_svc.get_checkout_preview(
            user_id=test_env["customer"].id,
            event_id=event_id,
        )
        assert preview_res["success"] is True
        assert preview_res["data"]["final_amount"] == 100.00

        confirm_res = bk_svc.confirm_booking(
            user_id=test_env["customer"].id,
            event_id=event_id,
        )
        assert confirm_res["success"] is True
        assert confirm_res["status"] == 201

    # 18. Status survives database save and reload
    def test_status_survives_db_reload(self, test_env, db_session):
        svc = EventService()
        res = svc.create_event({
            "title": "Persistence Test Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=15)),
            "start_time": "19:00",
            "status": "published",
        })
        event_id = res["data"]["id"]

        # Query clean from session
        db_session.expire_all()
        reloaded_ev = db_session.get(Event, event_id)
        assert reloaded_ev is not None
        assert reloaded_ev.status == "published"

    # 19. Existing event update without status change preserves current status
    def test_update_without_status_preserves_current_status(self, test_env):
        svc = EventService()
        create_res = svc.create_event({
            "title": "Preserve Status Event",
            "category_id": test_env["category"].id,
            "venue_id": test_env["venue"].id,
            "created_by": test_env["admin"].id,
            "event_date": str(date.today() + timedelta(days=10)),
            "start_time": "19:00",
            "status": "published",
        })
        event_id = create_res["data"]["id"]

        update_res = svc.update_event(event_id, {"title": "Updated Title Only"})
        assert update_res["success"] is True
        assert update_res["data"]["title"] == "Updated Title Only"
        assert update_res["data"]["status"] == "published"
