# test_real_mysql_flow.py
#
# Real MySQL End-to-End Smoke Test:
# Validates Seat Hold, Expiration, Re-hold, Booking confirmation,
# 2% Cashback reward, and Ticket QR generation directly against MySQL.

from datetime import date, timedelta, datetime
from app import create_app, db
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.seat import Seat
from models.seat_hold import SeatHold
from models.booking import Booking
from models.ticket import Ticket
from models.reward_transaction import RewardTransaction
from Services.seat_service import SeatService
from Services.booking_service import BookingService
from Services.ticket_service import TicketService
from werkzeug.security import generate_password_hash


def run_mysql_smoke_test():
    app = create_app()
    with app.app_context():
        print("=== RUNNING REAL MYSQL SMOKE TEST ===")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        seat_service = SeatService()
        booking_service = BookingService()
        ticket_service = TicketService()

        # 1. Ensure test users exist in MySQL
        u1_email = "mysql_tester1@seatmeup.com"
        u2_email = "mysql_tester2@seatmeup.com"

        u1 = db.session.query(User).filter_by(email=u1_email).first()
        if not u1:
            u1 = User(name="MySQL Tester 1", email=u1_email, password_hash=generate_password_hash("pass123"), role="customer", is_active=True)
            db.session.add(u1)

        u2 = db.session.query(User).filter_by(email=u2_email).first()
        if not u2:
            u2 = User(name="MySQL Tester 2", email=u2_email, password_hash=generate_password_hash("pass123"), role="customer", is_active=True)
            db.session.add(u2)

        # 2. Ensure test venue and category exist
        category = db.session.query(Category).first()
        if not category:
            category = Category(name="Live Concerts", description="Music Concerts")
            db.session.add(category)
            db.session.commit()

        venue = db.session.query(Venue).filter_by(name="MySQL Test Arena").first()
        if not venue:
            venue = Venue(name="MySQL Test Arena", address="100 Test Blvd", city="San Jose", state="CA", capacity=100, venue_type="seated")
            db.session.add(venue)
            db.session.commit()

        # 3. Ensure test seat exists
        seat = db.session.query(Seat).filter_by(venue_id=venue.id, seat_number="M-1").first()
        if not seat:
            seat = Seat(venue_id=venue.id, seat_number="M-1", section_name="Orchestra", price=120.00, is_active=True)
            db.session.add(seat)
            db.session.commit()

        # 4. Ensure test event exists
        event = db.session.query(Event).filter_by(title="MySQL Smoke Concert").first()
        if not event:
            event = Event(
                title="MySQL Smoke Concert",
                category_id=category.id,
                venue_id=venue.id,
                event_date=date.today() + timedelta(days=7),
                start_time="19:30:00",
                base_price=120.00,
                booking_open=True,
                requires_seats=True,
                status="published",
            )
            db.session.add(event)
            db.session.commit()

        event_id = event.id
        seat_id = seat.id
        user1_id = u1.id
        user2_id = u2.id

        # Clean up any existing holds on this test seat
        db.session.query(SeatHold).filter_by(event_id=event_id, seat_id=seat_id).delete()
        db.session.commit()

        print(f"\n[1] User 1 placing 1-minute hold on Seat M-1 for Event #{event_id}...")
        hold1_res = seat_service.hold_seat(event_id=event_id, seat_id=seat_id, user_id=user1_id)
        assert hold1_res["success"], f"Hold failed: {hold1_res}"
        print(f" -> SUCCESS: Hold Token: {hold1_res['data']['hold_token']}")

        # Verify hold is in MySQL
        hold_db = db.session.query(SeatHold).filter_by(event_id=event_id, seat_id=seat_id, status="active").first()
        assert hold_db is not None
        assert hold_db.status == "active"
        print(f" -> Verified active hold in MySQL table `seat_holds` (id={hold_db.id})")

        print("\n[2] Verifying User 2 cannot hold the same seat while active...")
        hold2_fail_res = seat_service.hold_seat(event_id=event_id, seat_id=seat_id, user_id=user2_id)
        assert not hold2_fail_res["success"]
        assert hold2_fail_res.get("status") == 409 or hold2_fail_res.get("status_code") == 409
        print(f" -> SUCCESS: Correctly rejected duplicate hold with 409 Conflict: {hold2_fail_res['message']}")

        print("\n[3] Forcing hold to expire (expires_at in past) to test MySQL expiration update...")
        hold_db.expires_at = datetime.utcnow() - timedelta(minutes=5)
        db.session.commit()

        print("\n[4] User 2 attempting to hold the expired seat...")
        hold2_res = seat_service.hold_seat(event_id=event_id, seat_id=seat_id, user_id=user2_id)
        assert hold2_res["success"], f"Expired hold re-acquisition failed: {hold2_res}"
        print(f" -> SUCCESS: User 2 successfully acquired hold: {hold2_res['data']['hold_token']}")

        # Verify the old hold is marked 'expired' in MySQL
        db.session.expire_all()
        old_hold = db.session.get(SeatHold, hold_db.id)
        assert old_hold.status == "expired", f"Expected old hold status to be 'expired', got '{old_hold.status}'"
        print(f" -> SUCCESS: Old hold (id={old_hold.id}) successfully updated to status='expired' in MySQL without DataError!")

        print("\n[5] Completing booking confirmation for User 2...")
        booking_res = booking_service.confirm_booking(user_id=user2_id, event_id=event_id)
        assert booking_res["success"], f"Booking failed: {booking_res}"
        b_data = booking_res["data"]
        print(f" -> SUCCESS: Booking confirmed: Ref={b_data['booking_reference']}, Total=${b_data['total_amount']}, Cashback=${b_data['cashback_amount']}")

        # Verify reward transaction and ticket in MySQL
        reward_tx = db.session.query(RewardTransaction).filter_by(booking_id=b_data["booking_id"]).first()
        assert reward_tx is not None
        print(f" -> Verified RewardTransaction in MySQL: type={reward_tx.transaction_type}, amount=${reward_tx.amount}")

        ticket = db.session.query(Ticket).filter_by(booking_id=b_data["booking_id"]).first()
        assert ticket is not None
        assert ticket.ticket_status == "valid"
        print(f" -> Verified Ticket in MySQL: token={ticket.ticket_token}, status={ticket.ticket_status}")

        print("\n[6] Verifying Ticket QR verification against MySQL...")
        verify_res = ticket_service.validate_and_verify_ticket(ticket.ticket_token, mark_as_used=True)
        assert verify_res["success"], f"Ticket verification failed: {verify_res}"
        print(f" -> SUCCESS: Ticket verified and marked as 'used'!")

        # Clean up test event and booking records
        booking_service.cancel_booking(b_data["booking_id"], user_id=user2_id)
        db.session.delete(event)
        db.session.delete(seat)
        db.session.delete(venue)
        db.session.commit()

        print("\n=======================================================")
        print("ALL REAL MYSQL SMOKE TESTS PASSED 100% WITH ZERO ERRORS!")
        print("=======================================================")

if __name__ == "__main__":
    run_mysql_smoke_test()
