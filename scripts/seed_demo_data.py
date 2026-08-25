"""SeatMeUp — Demo Data Seeding Script (Idempotent)

Seeds the database with realistic demo data:
- Categories (Concerts, Theatre, Comedy, Festivals, Sports)
- Venues (Seated & General Admission) with configured seat grids
- Events (Published Seated, Published GA, Draft) with add-ons
- Promo Codes (WELCOME10, SAVE200, MUSIC15, EXPIRED50, INACTIVE20)
- Demo Users (Admin, Alice Johnson with reward balance, John Doe)

Usage:
    python scripts/seed_demo_data.py
"""

import os
import sys
from datetime import date, datetime, time, timedelta
from werkzeug.security import generate_password_hash

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from models.category import Category
from models.venue import Venue
from models.seat import Seat
from models.event import Event
from models.event_addon import EventAddon
from models.promo_code import PromoCode
from models.user import User


def seed_data():
    app = create_app()
    with app.app_context():
        print("=" * 65)
        print("SEATMEUP — SEEDING DEMO DATA")
        print("=" * 65)

        # ---------------------------------------------------------
        # 1. Users (Admin + Customers)
        # ---------------------------------------------------------
        users_data = [
            {
                "name": "Admin User",
                "email": "admin@seatmeup.com",
                "password": "Admin@123",
                "role": "admin",
                "phone": "+91 99999 00001",
                "reward_balance": 0.00,
            },
            {
                "name": "Alice Johnson",
                "email": "customer@example.com",
                "password": "Customer@123",
                "role": "customer",
                "phone": "+91 98765 43210",
                "reward_balance": 50.00,
            },
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "Customer@123",
                "role": "customer",
                "phone": "+91 91234 56789",
                "reward_balance": 0.00,
            },
        ]

        seeded_users = {}
        for u_data in users_data:
            existing = User.query.filter_by(email=u_data["email"]).first()
            if not existing:
                user = User(
                    name=u_data["name"],
                    email=u_data["email"],
                    password_hash=generate_password_hash(u_data["password"]),
                    role=u_data["role"],
                    phone=u_data["phone"],
                    reward_balance=u_data["reward_balance"],
                    is_active=True,
                )
                db.session.add(user)
                db.session.flush()
                seeded_users[u_data["email"]] = user
                print(f"  [+] Created User: {u_data['email']} ({u_data['role']})")
            else:
                seeded_users[u_data["email"]] = existing
                print(f"  [.] User exists: {u_data['email']}")

        admin_user = seeded_users["admin@seatmeup.com"]

        # ---------------------------------------------------------
        # 2. Categories
        # ---------------------------------------------------------
        categories_data = [
            {"name": "Concerts", "description": "Live music performances and classical orchestra"},
            {"name": "Theatre & Plays", "description": "Drama, musicals, and Broadway productions"},
            {"name": "Comedy Shows", "description": "Stand-up comedy specials and open mics"},
            {"name": "Festivals", "description": "Multi-day music, art, and cultural celebrations"},
            {"name": "Sports", "description": "Stadium matches, esports tournaments, and athletic meets"},
        ]

        seeded_categories = {}
        for cat in categories_data:
            existing = Category.query.filter_by(name=cat["name"]).first()
            if not existing:
                c = Category(name=cat["name"], description=cat["description"])
                db.session.add(c)
                db.session.flush()
                seeded_categories[cat["name"]] = c
                print(f"  [+] Created Category: {cat['name']}")
            else:
                seeded_categories[cat["name"]] = existing
                print(f"  [.] Category exists: {cat['name']}")

        # ---------------------------------------------------------
        # 3. Venues & Seats
        # ---------------------------------------------------------
        venues_data = [
            {
                "name": "Grand Symphony Hall",
                "address": "100 Royal Avenue, Marine Lines",
                "city": "Mumbai",
                "state": "Maharashtra",
                "capacity": 50,
                "venue_type": "seated",
                "rows": 5,
                "seats_per_row": 10,
            },
            {
                "name": "Metropolis Arena",
                "address": "45 Stadium Way, Koramangala",
                "city": "Bengaluru",
                "state": "Karnataka",
                "capacity": 40,
                "venue_type": "seated",
                "rows": 4,
                "seats_per_row": 10,
            },
            {
                "name": "Sunset Open Grounds",
                "address": "Beachside Park, Candolim",
                "city": "Goa",
                "state": "Goa",
                "capacity": 500,
                "venue_type": "general_admission",
                "rows": 0,
                "seats_per_row": 0,
            },
            {
                "name": "Downtown Promenade",
                "address": "400 Main Street, Arts District",
                "city": "Mumbai",
                "state": "Maharashtra",
                "capacity": 1000,
                "venue_type": "general_admission",
                "rows": 0,
                "seats_per_row": 0,
            },
            {
                "name": "Lucia Club",
                "address": "88 Nightlife Boulevard, Bandra West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "capacity": 300,
                "venue_type": "general_admission",
                "rows": 0,
                "seats_per_row": 0,
            },
            {
                "name": "Borcelle Hall",
                "address": "12 Heritage Lane, Indiranagar",
                "city": "Bengaluru",
                "state": "Karnataka",
                "capacity": 50,
                "venue_type": "seated",
                "rows": 5,
                "seats_per_row": 10,
            },
            {
                "name": "San Bernardino Grounds",
                "address": "National Park Road, Candolim",
                "city": "Goa",
                "state": "Goa",
                "capacity": 2500,
                "venue_type": "general_admission",
                "rows": 0,
                "seats_per_row": 0,
            },
            {
                "name": "Daniel Stadium",
                "address": "Stadium Road, Sector 5",
                "city": "Delhi",
                "state": "Delhi",
                "capacity": 80,
                "venue_type": "seated",
                "rows": 8,
                "seats_per_row": 10,
            },
        ]

        seeded_venues = {}
        for v_data in venues_data:
            venue = Venue.query.filter_by(name=v_data["name"]).first()
            if not venue:
                venue = Venue(
                    name=v_data["name"],
                    address=v_data["address"],
                    city=v_data["city"],
                    state=v_data["state"],
                    capacity=v_data["capacity"],
                    venue_type=v_data["venue_type"],
                )
                db.session.add(venue)
                db.session.flush()
                print(f"  [+] Created Venue: {v_data['name']} ({v_data['venue_type']})")
            else:
                print(f"  [.] Venue exists: {v_data['name']}")

            seeded_venues[v_data["name"]] = venue

            # Generate default seating grid if seated and empty
            if v_data["rows"] > 0:
                existing_seats_count = Seat.query.filter_by(venue_id=venue.id).count()
                if existing_seats_count == 0:
                    for row_idx in range(v_data["rows"]):
                        row_letter = chr(65 + row_idx)
                        section = "VIP" if row_idx == 0 else "Orchestra"
                        price_override = 1000.00 if row_idx == 0 else 0.00
                        for seat_num in range(1, v_data["seats_per_row"] + 1):
                            seat = Seat(
                                venue_id=venue.id,
                                seat_number=f"{row_letter}{seat_num}",
                                section_name=section,
                                seat_type="vip" if row_idx == 0 else "standard",
                                price=price_override,
                                is_active=True,
                            )
                            db.session.add(seat)
                    db.session.flush()
                    print(f"      -> Configured {v_data['rows'] * v_data['seats_per_row']} seats for {v_data['name']}")

        # ---------------------------------------------------------
        # 4. Events & Addons
        # ---------------------------------------------------------
        now = datetime.utcnow()
        events_data = [
            {
                "title": "Street Fair 2028",
                "description": "5th Anniversary Street Fair! Food, Crafts, and Fun for the Whole Family featuring outdoor food vendors, live entertainment, and free drinks with admission.",
                "category": "Festivals",
                "venue": "Downtown Promenade",
                "date": date(2028, 11, 24),
                "start_time": time(8, 0),
                "end_time": time(21, 0),
                "base_price": 150.00,
                "poster": "/static/uploads/event_posters/image1.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": False,
                "addons": [
                    {"name": "VIP Fast-Track Pass", "price": 200.00, "qty": 50},
                    {"name": "Food & Beverage Tasting Voucher", "price": 150.00, "qty": 100},
                ],
            },
            {
                "title": "Dance Party Night",
                "description": "A vibrant nightlife dance party featuring top DJ line-up DJ Koran & DJ Perez with energetic futuristic visuals and dynamic light shows.",
                "category": "Concerts",
                "venue": "Lucia Club",
                "date": date(2030, 12, 24),
                "start_time": time(23, 0),
                "end_time": time(4, 0),
                "base_price": 500.00,
                "poster": "/static/uploads/event_posters/image2.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": False,
                "addons": [
                    {"name": "VIP Table & Bottle Service", "price": 1500.00, "qty": 10},
                    {"name": "Express Club Entry Pass", "price": 250.00, "qty": 50},
                ],
            },
            {
                "title": "Avery Turns 26: Birthday Bash",
                "description": "Bold, playful celebration with laughs and late-night fun! Featuring live DJ, starburst visuals, disco ball dance floor, and birthday cake toast.",
                "category": "Comedy Shows",
                "venue": "Borcelle Hall",
                "date": (now + timedelta(days=5)).date(),
                "start_time": time(20, 0),
                "end_time": time(1, 0),
                "base_price": 350.00,
                "poster": "/static/uploads/event_posters/image3.webp",
                "status": "published",
                "booking_open": True,
                "requires_seats": True,
                "addons": [
                    {"name": "Celebration Cake & Champagne Toast", "price": 200.00, "qty": 30},
                    {"name": "Polaroid Photo Souvenir", "price": 100.00, "qty": 50},
                ],
            },
            {
                "title": "Nocturnal Wonderland Festival",
                "description": "Step into Nocturnal Wonderland, a vibrant multi-day festival where electronic music, immersive art installations, and nightlife collide under colorful lights.",
                "category": "Festivals",
                "venue": "San Bernardino Grounds",
                "date": (now + timedelta(days=30)).date(),
                "start_time": time(17, 0),
                "end_time": time(23, 30),
                "base_price": 1500.00,
                "poster": "/static/uploads/event_posters/image4.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": False,
                "addons": [
                    {"name": "Weekend Camping Pass", "price": 750.00, "qty": 100},
                    {"name": "Official Festival Merchandise Pack", "price": 500.00, "qty": 150},
                ],
            },
            {
                "title": "Live Music Night at Daniel Stadium",
                "description": "An unforgettable night of live music and incredible performances featuring Alex Band, Garry Music, Smith Marco, and Silva Silva.",
                "category": "Concerts",
                "venue": "Daniel Stadium",
                "date": (now + timedelta(days=45)).date(),
                "start_time": time(18, 30),
                "end_time": time(22, 30),
                "base_price": 850.00,
                "poster": "/static/uploads/event_posters/image5.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": True,
                "addons": [
                    {"name": "Backstage Meet & Greet", "price": 1200.00, "qty": 20},
                    {"name": "Fan Pit Access Wristband", "price": 600.00, "qty": 40},
                ],
            },
            {
                "title": "Tropical Purple Party",
                "description": "Dance the night away surrounded by tropical vibes and purple lights with featured artists DJ Francois & DJ Sebastian.",
                "category": "Concerts",
                "venue": "Lucia Club",
                "date": (now + timedelta(days=6)).date(),
                "start_time": time(21, 0),
                "end_time": time(2, 0),
                "base_price": 400.00,
                "poster": "/static/uploads/event_posters/image6.webp",
                "status": "published",
                "booking_open": True,
                "requires_seats": False,
                "addons": [
                    {"name": "Tropical Cocktail Pitcher", "price": 350.00, "qty": 60},
                    {"name": "VIP Balcony Access", "price": 500.00, "qty": 25},
                ],
            },
            {
                "title": "Symphony Under The Stars",
                "description": "An enchanting evening of classical orchestral masterpieces conducted by world-renowned maestros with full string and brass ensembles.",
                "category": "Concerts",
                "venue": "Grand Symphony Hall",
                "date": (now + timedelta(days=25)).date(),
                "start_time": time(19, 30),
                "end_time": time(22, 0),
                "base_price": 750.00,
                "poster": "/static/uploads/event_posters/image1.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": True,
                "addons": [
                    {"name": "VIP Lounge & Complimentary Champagne", "price": 499.00, "qty": 30},
                    {"name": "Official Commemorative Programme Book", "price": 150.00, "qty": 100},
                    {"name": "Reserved Premium Parking Pass", "price": 200.00, "qty": 20},
                ],
            },
            {
                "title": "Neon Beats EDM Festival 2026",
                "description": "The ultimate electronic dance music experience featuring top international DJs, massive laser displays, and vibrant festival vibes.",
                "category": "Festivals",
                "venue": "Sunset Open Grounds",
                "date": (now + timedelta(days=40)).date(),
                "start_time": time(17, 0),
                "end_time": time(23, 30),
                "base_price": 1200.00,
                "poster": "/static/uploads/event_posters/image4.jpg",
                "status": "published",
                "booking_open": True,
                "requires_seats": False,
                "addons": [
                    {"name": "LED Festival Glow Wristband", "price": 250.00, "qty": 200},
                    {"name": "Unlimited Beverage Access Pass", "price": 800.00, "qty": 150},
                ],
            },
            {
                "title": "Laugh Riot Standup Showcase",
                "description": "An intimate evening with five of the nation's sharpest stand-up comedians delivering brand-new punchlines and observational comedy.",
                "category": "Comedy Shows",
                "venue": "Metropolis Arena",
                "date": (now + timedelta(days=15)).date(),
                "start_time": time(20, 0),
                "end_time": time(22, 0),
                "base_price": 450.00,
                "poster": "/static/uploads/event_posters/image3.webp",
                "status": "published",
                "booking_open": True,
                "requires_seats": True,
                "addons": [
                    {"name": "Meet & Greet Comic Backstage Pass", "price": 350.00, "qty": 15},
                ],
            },
            {
                "title": "Broadway Echoes Musical",
                "description": "Upcoming theatrical production rehearsing for autumn debut.",
                "category": "Theatre & Plays",
                "venue": "Grand Symphony Hall",
                "date": (now + timedelta(days=60)).date(),
                "start_time": time(18, 0),
                "end_time": time(21, 0),
                "base_price": 600.00,
                "poster": "/static/uploads/event_posters/image5.jpg",
                "status": "unpublished",
                "booking_open": False,
                "requires_seats": True,
                "addons": [],
            },
        ]

        for e_data in events_data:
            existing_event = Event.query.filter_by(title=e_data["title"]).first()
            if not existing_event:
                cat = seeded_categories[e_data["category"]]
                ven = seeded_venues[e_data["venue"]]
                event = Event(
                    title=e_data["title"],
                    description=e_data["description"],
                    category_id=cat.id,
                    venue_id=ven.id,
                    created_by=admin_user.id,
                    event_date=e_data["date"],
                    start_time=e_data["start_time"],
                    end_time=e_data["end_time"],
                    base_price=e_data["base_price"],
                    poster=e_data.get("poster"),
                    status=e_data["status"],
                    booking_open=e_data["booking_open"],
                    requires_seats=e_data["requires_seats"],
                )
                db.session.add(event)
                db.session.flush()
                print(f"  [+] Created Event: {e_data['title']} ({e_data['status']})")

                for addon_info in e_data["addons"]:
                    addon = EventAddon(
                        event_id=event.id,
                        name=addon_info["name"],
                        price=addon_info["price"],
                        available_quantity=addon_info["qty"],
                        is_active=True,
                    )
                    db.session.add(addon)
                db.session.flush()
            else:
                if not existing_event.poster and e_data.get("poster"):
                    existing_event.poster = e_data["poster"]
                print(f"  [.] Event exists: {e_data['title']}")

        # ---------------------------------------------------------
        # 5. Promo Codes
        # ---------------------------------------------------------
        promo_codes_data = [
            {
                "code": "WELCOME10",
                "description": "10% off for all demo ticket bookings",
                "discount_type": "percentage",
                "discount_value": 10.00,
                "minimum_booking_amount": 0.00,
                "max_uses": 500,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
            {
                "code": "SAVE200",
                "description": "Flat ₹200 off on orders above ₹1,000",
                "discount_type": "fixed",
                "discount_value": 200.00,
                "minimum_booking_amount": 1000.00,
                "max_uses": 200,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
            {
                "code": "MUSIC15",
                "description": "15% off on music concerts & festivals (min ₹500)",
                "discount_type": "percentage",
                "discount_value": 15.00,
                "minimum_booking_amount": 500.00,
                "max_uses": 100,
                "valid_until": now + timedelta(days=180),
                "is_active": True,
            },
            {
                "code": "EXPIRED50",
                "description": "Expired promotional voucher for QA testing",
                "discount_type": "percentage",
                "discount_value": 50.00,
                "minimum_booking_amount": 0.00,
                "max_uses": 50,
                "valid_until": now - timedelta(days=30),  # Expired
                "is_active": True,
            },
            {
                "code": "INACTIVE20",
                "description": "Deactivated promotional voucher for QA testing",
                "discount_type": "percentage",
                "discount_value": 20.00,
                "minimum_booking_amount": 0.00,
                "max_uses": 50,
                "valid_until": now + timedelta(days=90),
                "is_active": False,  # Deactivated
            },
            {
                "code": "MAXED100",
                "description": "Maxed-out promotional voucher for QA limit testing",
                "discount_type": "fixed",
                "discount_value": 100.00,
                "minimum_booking_amount": 0.00,
                "max_uses": 5,
                "used_count": 5,  # Maxed out
                "valid_until": now + timedelta(days=90),
                "is_active": True,
            },
        ]

        for p_data in promo_codes_data:
            existing_promo = PromoCode.query.filter_by(code=p_data["code"]).first()
            if not existing_promo:
                promo = PromoCode(
                    code=p_data["code"],
                    description=p_data["description"],
                    discount_type=p_data["discount_type"],
                    discount_value=p_data["discount_value"],
                    minimum_booking_amount=p_data["minimum_booking_amount"],
                    max_uses=p_data["max_uses"],
                    used_count=p_data.get("used_count", 0),
                    valid_from=now - timedelta(days=1),
                    valid_until=p_data["valid_until"],
                    is_active=p_data["is_active"],
                )
                db.session.add(promo)
                print(f"  [+] Created Promo Code: {p_data['code']} ({p_data['discount_type']} - {p_data['discount_value']})")
        # ---------------------------------------------------------
        # 6. Mock Bookings & Tickets for Demo
        # ---------------------------------------------------------
        from models.booking import Booking
        from models.booking_item import BookingItem
        from models.booking_addon import BookingAddon
        from models.ticket import Ticket
        import uuid

        alice = seeded_users.get("customer@example.com")
        john = seeded_users.get("john.doe@example.com")

        # Booking 1: Alice -> Tropical Purple Party
        tp_event = Event.query.filter_by(title="Tropical Purple Party").first()
        if alice and tp_event and not Booking.query.filter_by(booking_reference="SMU-DEMO-TP01").first():
            b1 = Booking(
                user_id=alice.id,
                event_id=tp_event.id,
                booking_reference="SMU-DEMO-TP01",
                total_amount=1035.00,
                status="confirmed",
                booked_at=now - timedelta(days=2),
            )
            db.session.add(b1)
            db.session.flush()

            bi1 = BookingItem(
                booking_id=b1.id,
                item_type="ticket",
                quantity=2,
                unit_price=400.00,
                total_price=800.00,
            )
            db.session.add(bi1)

            # Addon
            tp_addon = EventAddon.query.filter_by(event_id=tp_event.id, name="Tropical Cocktail Pitcher").first()
            if tp_addon:
                ba1 = BookingAddon(
                    booking_id=b1.id,
                    addon_id=tp_addon.id,
                    quantity=1,
                    unit_price=350.00,
                    total_price=350.00,
                )
                db.session.add(ba1)

            # Ticket
            token1 = f"TKT-{uuid.uuid4().hex[:12].upper()}"
            t1 = Ticket(
                booking_id=b1.id,
                ticket_token=token1,
                ticket_status="valid",
                qr_data=f"SEATMEUP:{b1.booking_reference}:{token1}",
                issued_at=now - timedelta(days=2),
            )
            db.session.add(t1)
            print(f"  [+] Created Demo Booking: {b1.booking_reference} for {alice.name}")

        # Booking 2: John Doe -> Street Fair 2028
        sf_event = Event.query.filter_by(title="Street Fair 2028").first()
        if john and sf_event and not Booking.query.filter_by(booking_reference="SMU-DEMO-SF01").first():
            b2 = Booking(
                user_id=john.id,
                event_id=sf_event.id,
                booking_reference="SMU-DEMO-SF01",
                total_amount=450.00,
                status="confirmed",
                booked_at=now - timedelta(days=1),
            )
            db.session.add(b2)
            db.session.flush()

            bi2 = BookingItem(
                booking_id=b2.id,
                item_type="ticket",
                quantity=2,
                unit_price=150.00,
                total_price=300.00,
            )
            db.session.add(bi2)

            sf_addon = EventAddon.query.filter_by(event_id=sf_event.id, name="Food & Beverage Tasting Voucher").first()
            if sf_addon:
                ba2 = BookingAddon(
                    booking_id=b2.id,
                    addon_id=sf_addon.id,
                    quantity=1,
                    unit_price=150.00,
                    total_price=150.00,
                )
                db.session.add(ba2)

            token2 = f"TKT-{uuid.uuid4().hex[:12].upper()}"
            t2 = Ticket(
                booking_id=b2.id,
                ticket_token=token2,
                ticket_status="valid",
                qr_data=f"SEATMEUP:{b2.booking_reference}:{token2}",
                issued_at=now - timedelta(days=1),
            )
            db.session.add(t2)
            print(f"  [+] Created Demo Booking: {b2.booking_reference} for {john.name}")

        # Booking 3: Alice -> Avery Turns 26: Birthday Bash (Seated)
        av_event = Event.query.filter_by(title="Avery Turns 26: Birthday Bash").first()
        if alice and av_event and not Booking.query.filter_by(booking_reference="SMU-DEMO-AV01").first():
            bh_venue = Venue.query.filter_by(name="Borcelle Hall").first()
            bh_seats = Seat.query.filter_by(venue_id=bh_venue.id).all() if bh_venue else []
            if bh_seats:
                b3 = Booking(
                    user_id=alice.id,
                    event_id=av_event.id,
                    booking_reference="SMU-DEMO-AV01",
                    total_amount=2200.00,
                    status="confirmed",
                    booked_at=now - timedelta(hours=12),
                )
                db.session.add(b3)
                db.session.flush()

                bi3_1 = BookingItem(
                    booking_id=b3.id,
                    seat_id=bh_seats[0].id,
                    item_type="ticket",
                    quantity=1,
                    unit_price=1000.00,
                    total_price=1000.00,
                )
                bi3_2 = BookingItem(
                    booking_id=b3.id,
                    seat_id=bh_seats[1].id,
                    item_type="ticket",
                    quantity=1,
                    unit_price=1000.00,
                    total_price=1000.00,
                )
                db.session.add_all([bi3_1, bi3_2])

                av_addon = EventAddon.query.filter_by(event_id=av_event.id, name="Celebration Cake & Champagne Toast").first()
                if av_addon:
                    ba3 = BookingAddon(
                        booking_id=b3.id,
                        addon_id=av_addon.id,
                        quantity=1,
                        unit_price=200.00,
                        total_price=200.00,
                    )
                    db.session.add(ba3)

                token3 = f"TKT-{uuid.uuid4().hex[:12].upper()}"
                t3 = Ticket(
                    booking_id=b3.id,
                    ticket_token=token3,
                    ticket_status="valid",
                    qr_data=f"SEATMEUP:{b3.booking_reference}:{token3}",
                    issued_at=now - timedelta(hours=12),
                )
                db.session.add(t3)
                print(f"  [+] Created Demo Booking: {b3.booking_reference} for {alice.name}")

        db.session.commit()

        print("\n" + "=" * 65)
        print("SEEDING COMPLETE! READY FOR DEMO & TESTING")
        print("=" * 65)
        print("\nDEMO USER CREDENTIALS:")
        print("  Admin:     admin@seatmeup.com    / Admin@123    (Full Admin Access)")
        print("  Customer:  customer@example.com  / Customer@123 (Reward Balance: Rs. 50.00)")
        print("  Customer:  john.doe@example.com  / Customer@123 (Fresh Customer)")
        print("\nACTIVE PROMO CODES:")
        print("  WELCOME10  -> 10% off (No minimum spend)")
        print("  SAVE200    -> Rs. 200 off (Min spend Rs. 1,000)")
        print("  MUSIC15    -> 15% off (Min spend Rs. 500)")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    seed_data()
