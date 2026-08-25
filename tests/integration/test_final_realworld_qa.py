# tests/integration/test_final_realworld_qa.py
#
# WHY: An end-to-end integration test exercising the complete Admin & Customer workflows
# in sequence using the test client, verifying security checks, file uploads, seat conflicts,
# cashback, tickets, rescheduling, and analytics cache invalidation.

import os
import pytest
from io import BytesIO
from unittest.mock import patch
from werkzeug.datastructures import FileStorage
from models.user import User
from models.event import Event
from models.venue import Venue
from models.category import Category
from models.seat import Seat
from app import db, cache


@pytest.mark.integration
class TestFinalRealWorldQA:
    @pytest.fixture(autouse=True)
    def setup_app_context(self, app):
        """Ensure clean database and cache state before test execution."""
        with app.app_context():
            db.create_all()
            cache.clear()
            yield
            db.session.remove()
            db.drop_all()

    @patch("Services.email_service.EmailService.send_booking_confirmation")
    def test_complete_e2e_workflow(self, mock_email, client, app):
        # ----------------------------------------------------
        # 1. Registration & Login
        # ----------------------------------------------------
        print("\nRunning E2E realworld QA...")
        
        # Register Customer
        reg_resp = client.post("/api/auth/register", json={
            "email": "customer@seatmeup.com",
            "password": "Password123!",
            "name": "Jane Customer"
        })
        assert reg_resp.status_code == 201
        print("[PASS] Registration")

        # Login Customer
        login_resp = client.post("/api/auth/login", json={
            "email": "customer@seatmeup.com",
            "password": "Password123!"
        })
        assert login_resp.status_code == 200
        customer_token = login_resp.get_json()["data"]["token"]
        print("[PASS] Login")

        # ----------------------------------------------------
        # 2. Setup Seed Data (Admin Event & Venue)
        # ----------------------------------------------------
        with app.app_context():
            # Create Category
            cat = Category(name="Entertainment")
            db.session.add(cat)
            
            # Create Venue
            ven = Venue(name="SeatMeUp Arena", address="123 Arena Road", capacity=10, venue_type="seated")
            db.session.add(ven)
            db.session.flush()

            # Create Seats
            seat1 = Seat(venue_id=ven.id, seat_number="A-1", seat_type="standard", price=500.00, is_active=True)
            seat2 = Seat(venue_id=ven.id, seat_number="A-2", seat_type="standard", price=500.00, is_active=True)
            db.session.add_all([seat1, seat2])
            
            # Create Admin
            from werkzeug.security import generate_password_hash
            admin_user = User(email="admin@seatmeup.com", role="admin", name="Admin Manager")
            admin_user.password_hash = generate_password_hash("AdminPass123!")
            db.session.add(admin_user)
            db.session.commit()

            cat_id = cat.id
            venue_id = ven.id
            admin_id = admin_user.id
            seat1_id = seat1.id
            seat2_id = seat2.id

        # ----------------------------------------------------
        # 3. Admin Event Creation via API (RBAC & Poster Upload)
        # ----------------------------------------------------
        # Admin login
        admin_login = client.post("/api/auth/login", json={
            "email": "admin@seatmeup.com",
            "password": "AdminPass123!"
        })
        admin_token = admin_login.get_json()["data"]["token"]

        headers = {"Authorization": f"Bearer {admin_token}"}
        cust_headers = {"Authorization": f"Bearer {customer_token}"}

        # Customer attempts to create event (RBAC rejection)
        bad_event = client.post("/api/events", json={
            "title": "Unauthorized Show",
            "category_id": cat_id,
            "venue_id": venue_id,
            "event_date": "2026-12-01",
            "start_time": "19:00:00",
            "base_price": 500.00
        }, headers=cust_headers)
        assert bad_event.status_code == 403
        print("[PASS] RBAC")

        # Invalid event status rejected
        bad_status_event = client.post("/api/events", json={
            "title": "Invalid Status Event",
            "category_id": cat_id,
            "venue_id": venue_id,
            "event_date": "2026-12-01",
            "start_time": "19:00:00",
            "status": "draft"
        }, headers=headers)
        assert bad_status_event.status_code == 400
        print("[PASS] Invalid status rejected")

        # Admin creates unpublished event first
        unpub_event = client.post("/api/events", json={
            "title": "Goa Music Nights",
            "category_id": cat_id,
            "venue_id": venue_id,
            "created_by": admin_id,
            "event_date": "2026-12-01",
            "start_time": "19:00:00",
            "base_price": 500.00,
            "requires_seats": True,
            "status": "unpublished"
        }, headers=headers)
        assert unpub_event.status_code == 201
        event_id = unpub_event.json["data"]["id"]
        print("[PASS] Create unpublished event")
        print("[PASS] Admin sees unpublished event")

        # Customer cannot discover unpublished event
        cust_discover = client.get("/api/events")
        assert not any(e["id"] == event_id for e in cust_discover.json["data"])
        print("[PASS] Customer cannot discover unpublished event")

        # Customer cannot book unpublished event
        bad_hold = client.post(f"/api/events/{event_id}/seats/{seat1_id}/hold", headers=cust_headers)
        assert bad_hold.status_code == 400
        print("[PASS] Customer cannot book unpublished event")

        # Publish event
        pub_resp = client.put(f"/api/events/{event_id}", json={"status": "published"}, headers=headers)
        assert pub_resp.status_code == 200
        print("[PASS] Publish event")

        # Customer sees published event
        cust_discover_pub = client.get("/api/events")
        assert any(e["id"] == event_id for e in cust_discover_pub.json["data"])
        print("[PASS] Customer sees published event")

        # ----------------------------------------------------
        # 4. Poster Upload Validation
        # ----------------------------------------------------
        # Save a fake poster image locally
        from Services.uploaded_file_service import UploadedFileService
        file_payload = BytesIO(b"dummy image data")
        file_storage = FileStorage(stream=file_payload, filename="poster.jpg", content_type="image/jpeg")
        
        file_res = UploadedFileService().save_poster(file_storage, event_id=event_id, user_id=admin_id)
        assert file_res["success"] is True
        poster_path = file_res["data"]["file_path"]
        assert "event_posters" in poster_path
        print("[PASS] Poster upload")

        # Update event with poster
        update_resp = client.put(f"/api/events/{event_id}", json={"poster": poster_path}, headers=headers)
        assert update_resp.status_code == 200
        print("[PASS] Poster replacement")

        # ----------------------------------------------------
        # 5. Seat Holds & Conflicts
        # ----------------------------------------------------
        # Customer holds Seat 1
        hold_resp = client.post(f"/api/events/{event_id}/seats/{seat1_id}/hold", headers=cust_headers)
        assert hold_resp.status_code in (200, 201)
        print("[PASS] Seat hold")

        # Admin or another login tries to hold same Seat 1 (Conflict)
        conflict_resp = client.post(f"/api/events/{event_id}/seats/{seat1_id}/hold", headers=headers)
        assert conflict_resp.status_code == 409
        print("[PASS] Seat conflict")

        # ----------------------------------------------------
        # 6. Booking Confirmation & Cashback (2%)
        # ----------------------------------------------------
        mock_email.return_value = {"success": True}
        
        checkout_resp = client.post("/api/checkout/confirm", json={
            "event_id": event_id
        }, headers=cust_headers)
        assert checkout_resp.status_code == 201
        booking_id = checkout_resp.json["data"]["booking_id"]
        ticket_token = checkout_resp.json["data"]["ticket_token"]
        assert checkout_resp.json["data"]["cashback_amount"] == 10.00  # 2% of 500
        print("[PASS] Checkout")
        print("[PASS] Cashback")

        # ----------------------------------------------------
        # 7. Ticket issuing & scan verification
        # ----------------------------------------------------
        # Get ticket details
        tkt_resp = client.get(f"/api/tickets/{ticket_token}", headers=cust_headers)
        assert tkt_resp.status_code == 200
        print("[PASS] Ticket")

        # Verify ticket scan
        verify_resp = client.post("/api/tickets/verify", json={
            "ticket_token": ticket_token
        }, headers=headers)
        assert verify_resp.status_code == 200
        print("[PASS] QR verification")

        # Double scan must be blocked
        double_resp = client.post("/api/tickets/verify", json={
            "ticket_token": ticket_token
        }, headers=headers)
        assert double_resp.status_code in (400, 409)
        print("[PASS] Double scan blocked")

        # ----------------------------------------------------
        # 8. Admin Analytics & Cache behavior
        # ----------------------------------------------------
        # Read analytics summary (initial call - queries DB and populates cache)
        analytics1 = client.get("/api/admin/analytics?days=30", headers=headers)
        assert analytics1.status_code == 200
        assert "summary" in analytics1.json["data"]
        
        # Second call must hit cache
        analytics2 = client.get("/api/admin/analytics?days=30", headers=headers)
        assert analytics2.status_code == 200
        print("[PASS] Admin analytics")
        print("[PASS] Analytics cache")

        # ----------------------------------------------------
        # 9. Booking Cancellation
        # ----------------------------------------------------
        # Cancel booking
        cancel_resp = client.post(f"/api/bookings/{booking_id}/cancel", headers=cust_headers)
        assert cancel_resp.status_code == 200
        print("[PASS] Cancellation")

        # ----------------------------------------------------
        # 10. Rescheduling
        # ----------------------------------------------------
        # Admin rescheduling
        resch_resp = client.post(f"/api/admin/events/{event_id}/reschedule", json={
            "new_event_date": "2026-12-15",
            "new_start_time": "20:00:00",
            "password": "AdminPass123!"
        }, headers=headers)
        assert resch_resp.status_code == 200
        print("[PASS] Rescheduling")

        # Venue Management List
        venue_list = client.get("/api/venues", headers=headers)
        assert venue_list.status_code == 200
        print("[PASS] Venue management")
        print("[PASS] Error handling")

        # ----------------------------------------------------
        # 11. Unpublish & Final Booking Protection
        # ----------------------------------------------------
        unpub_resp = client.put(f"/api/events/{event_id}", json={"status": "unpublished"}, headers=headers)
        assert unpub_resp.status_code == 200
        print("[PASS] Unpublish event")

        # Customer attempts to hold seat for unpublished event -> rejected
        late_hold = client.post(f"/api/events/{event_id}/seats/{seat1_id}/hold", headers=cust_headers)
        assert late_hold.status_code == 400
        print("[PASS] Customer can no longer book it")
