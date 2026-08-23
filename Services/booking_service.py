# Services/booking_service.py
#
# Business logic for Checkout, Booking Confirmation, Promo Code Application,
# and 2% Cashback Reward Calculation.
#
# Flow:
#   Controllers -> BookingService -> BookingDAO / SeatHoldDAO / PromoCodeDAO / etc. -> MySQL

from datetime import datetime
import uuid

from app import db
from DAO import (
    BookingDAO,
    BookingItemDAO,
    BookingAddonDAO,
    EventDAO,
    VenueDAO,
    SeatDAO,
    SeatHoldDAO,
    EventAddonDAO,
    PromoCodeDAO,
    PromoCodeUsageDAO,
    RewardTransactionDAO,
    UserDAO,
    TicketDAO,
)
from models.booking import Booking
from models.booking_item import BookingItem
from models.booking_addon import BookingAddon
from models.promo_code_usage import PromoCodeUsage
from models.reward_transaction import RewardTransaction
from models.ticket import Ticket
from api.serializers import booking_to_dict
from Services._result import ok, fail
from Services.promo_service import PromoCodeService


def _make_booking_reference():
    """Generate a unique booking reference, e.g. SMU-7D3C9A2B1F04."""
    return "SMU-" + uuid.uuid4().hex[:12].upper()


class BookingService:
    def __init__(self):
        self.booking_dao = BookingDAO()
        self.booking_item_dao = BookingItemDAO()
        self.booking_addon_dao = BookingAddonDAO()
        self.event_dao = EventDAO()
        self.venue_dao = VenueDAO()
        self.seat_dao = SeatDAO()
        self.seat_hold_dao = SeatHoldDAO()
        self.event_addon_dao = EventAddonDAO()
        self.promo_dao = PromoCodeDAO()
        self.promo_usage_dao = PromoCodeUsageDAO()
        self.reward_dao = RewardTransactionDAO()
        self.user_dao = UserDAO()
        self.ticket_dao = TicketDAO()
        self.promo_service = PromoCodeService()

    # ---------------------------------------------------------------- #
    # CHECKOUT PREVIEW & CALCULATION
    # ---------------------------------------------------------------- #
    def get_checkout_preview(
        self,
        user_id: int,
        event_id: int,
        promo_code: str | None = None,
        selected_addons: dict | None = None,
    ) -> dict:
        """Calculate and return checkout details for active held seats, addons, promo, and 2% cashback."""
        # 1. Validate Event & User
        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)

        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)

        # 2. Get active holds for this user and event
        now = datetime.utcnow()
        active_holds = self.seat_hold_dao.get_active_holds_by_user(user_id, event_id)
        if not active_holds:
            return fail("No active seat holds found. Please select your seats first.", 400)

        # Verify holds are not expired
        held_seat_items = []
        ticket_subtotal = 0.0
        min_remaining = 60

        for hold in active_holds:
            if hold.expires_at <= now or hold.status != "active":
                return fail("Your seat hold has expired. Please select your seats again.", 409)

            seat = self.seat_dao.get_seat_by_id(hold.seat_id)
            if seat is None or not seat.is_active:
                return fail("One or more selected seats are no longer available.", 409)

            rem = max(0, int((hold.expires_at - now).total_seconds()))
            if rem < min_remaining:
                min_remaining = rem

            seat_price = float(seat.price if seat.price and seat.price > 0 else (event.base_price or 0.0))
            ticket_subtotal += seat_price

            held_seat_items.append({
                "seat_id": seat.id,
                "seat_number": seat.seat_number,
                "section_name": seat.section_name or "General",
                "seat_type": seat.seat_type,
                "price": seat_price,
                "hold_token": hold.hold_token,
                "remaining_seconds": rem,
            })

        # 3. Available Event Addons
        all_event_addons = self.event_addon_dao.get_addons_by_event(event_id)
        addon_items = []
        addon_subtotal = 0.0
        selected_addons = selected_addons or {}

        for ea in all_event_addons:
            if not ea.is_active:
                continue
            qty = int(selected_addons.get(str(ea.id)) or selected_addons.get(ea.id) or 0)
            item_total = float(ea.price) * qty
            if qty > 0:
                addon_subtotal += item_total
            addon_items.append({
                "addon_id": ea.id,
                "name": ea.name,
                "description": ea.description,
                "unit_price": float(ea.price),
                "selected_quantity": qty,
                "total_price": round(item_total, 2),
            })

        # 4. Gross calculation
        ticket_subtotal = round(ticket_subtotal, 2)
        addon_subtotal = round(addon_subtotal, 2)
        gross_amount = round(ticket_subtotal + addon_subtotal, 2)

        # 5. Promo Code Discount
        discount_amount = 0.0
        promo_info = None
        promo_error = None

        if promo_code and promo_code.strip():
            promo_res = self.promo_service.validate_and_calculate_discount(
                code=promo_code,
                user_id=user_id,
                order_subtotal=gross_amount,
            )
            if promo_res.get("success"):
                promo_info = promo_res["data"]
                discount_amount = float(promo_info.get("discount_amount", 0.0))
            else:
                promo_error = promo_res.get("message")

        # 6. Final Amount & 2% Cashback
        final_amount = max(0.0, round(gross_amount - discount_amount, 2))
        cashback_amount = round(final_amount * 0.02, 2)

        return ok(
            "Checkout preview calculated",
            {
                "event_id": event.id,
                "event_title": event.title,
                "event_date": str(event.event_date),
                "start_time": str(event.start_time),
                "venue_id": event.venue_id,
                "held_seats": held_seat_items,
                "addons": addon_items,
                "ticket_subtotal": ticket_subtotal,
                "addon_subtotal": addon_subtotal,
                "gross_amount": gross_amount,
                "promo_applied": promo_info,
                "promo_error": promo_error,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "cashback_amount": cashback_amount,
                "min_remaining_seconds": min_remaining,
            },
        )

    # ---------------------------------------------------------------- #
    # CONFIRM BOOKING TRANSACTION
    # ---------------------------------------------------------------- #
    def confirm_booking(
        self,
        user_id: int,
        event_id: int,
        selected_addons: dict | list | None = None,
        promo_code: str | None = None,
    ) -> dict:
        """Confirm booking in one atomic database transaction with hold consumption, promo, and 2% reward."""
        now = datetime.utcnow()

        # Step 1: Validate User & Event
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)

        event = self.event_dao.get_event_by_id(event_id)
        if event is None:
            return fail("Event not found", 404)

        # Step 2: Validate Active Seat Holds
        active_holds = (
            self.seat_hold_dao.get_active_holds_by_user(user_id, event_id)
        )
        if not active_holds:
            return fail("No active seat holds found. Please select your seats again.", 400)

        # Check if any hold is expired
        held_seats = []
        ticket_subtotal = 0.0

        for hold in active_holds:
            if hold.expires_at <= now or hold.status != "active":
                return fail("Your seat hold has expired. Please select your seats again.", 409)

            seat = self.seat_dao.get_seat_by_id(hold.seat_id)
            if seat is None or not seat.is_active:
                return fail("One or more selected seats are no longer active.", 409)

            seat_price = float(seat.price if seat.price and seat.price > 0 else (event.base_price or 0.0))
            ticket_subtotal += seat_price
            held_seats.append((hold, seat, seat_price))

        # Check if any seat was already booked in the meantime
        for hold, seat, _ in held_seats:
            existing_booking_item = (
                BookingItem.query
                .join(Booking, BookingItem.booking_id == Booking.id)
                .filter(
                    Booking.event_id == event_id,
                    Booking.status.in_(["confirmed", "completed", "pending"]),
                    BookingItem.seat_id == seat.id,
                )
                .first()
            )
            if existing_booking_item is not None:
                return fail(f"Seat {seat.seat_number} has already been booked by another user.", 409)

        # Step 3: Calculate Addons
        parsed_addons = {}
        if isinstance(selected_addons, dict):
            parsed_addons = selected_addons
        elif isinstance(selected_addons, list):
            for item in selected_addons:
                if isinstance(item, dict) and "addon_id" in item:
                    parsed_addons[str(item["addon_id"])] = item.get("quantity", 1)

        addon_subtotal = 0.0
        addon_records_to_create = []
        for aid_str, qty in parsed_addons.items():
            try:
                aid = int(aid_str)
                qty = int(qty)
            except (ValueError, TypeError):
                continue

            if qty <= 0:
                continue

            addon = self.event_addon_dao.get_addon_by_id(aid)
            if addon and addon.event_id == event_id and addon.is_active:
                unit_p = float(addon.price)
                tot_p = round(unit_p * qty, 2)
                addon_subtotal += tot_p
                addon_records_to_create.append((addon, qty, unit_p, tot_p))

        gross_amount = round(ticket_subtotal + addon_subtotal, 2)

        # Step 4: Validate Promo Code
        promo = None
        discount_amount = 0.0
        if promo_code and promo_code.strip():
            promo_res = self.promo_service.validate_and_calculate_discount(
                code=promo_code,
                user_id=user_id,
                order_subtotal=gross_amount,
            )
            if not promo_res.get("success"):
                return fail(promo_res.get("message", "Invalid promo code"), 400)

            promo_data = promo_res["data"]
            discount_amount = float(promo_data["discount_amount"])
            promo = self.promo_dao.get_promo_by_id(promo_data["promo_id"])

        final_amount = max(0.0, round(gross_amount - discount_amount, 2))
        cashback_amount = round(final_amount * 0.02, 2)

        # Step 5: EXECUTE DATABASE TRANSACTION
        try:
            # 5a. Create Booking
            booking_ref = _make_booking_reference()
            booking = Booking(
                user_id=user_id,
                event_id=event_id,
                booking_reference=booking_ref,
                total_amount=final_amount,
                discount_amount=discount_amount,
                cashback_amount=cashback_amount,
                status="confirmed",
                booked_at=datetime.utcnow(),
            )
            db.session.add(booking)
            db.session.flush()  # Ensures booking.id is available

            # 5b. Create BookingItem for each held seat
            for hold, seat, seat_price in held_seats:
                b_item = BookingItem(
                    booking_id=booking.id,
                    seat_id=seat.id,
                    item_type="ticket",
                    quantity=1,
                    unit_price=seat_price,
                    total_price=seat_price,
                )
                db.session.add(b_item)

            # 5c. Create BookingAddon for each selected addon
            for addon, qty, unit_p, tot_p in addon_records_to_create:
                b_addon = BookingAddon(
                    booking_id=booking.id,
                    addon_id=addon.id,
                    quantity=qty,
                    unit_price=unit_p,
                    total_price=tot_p,
                )
                db.session.add(b_addon)

            # 5d. Record PromoCodeUsage & bump count if promo used
            if promo and discount_amount > 0:
                usage = PromoCodeUsage(
                    promo_code_id=promo.id,
                    user_id=user_id,
                    booking_id=booking.id,
                    discount_amount=discount_amount,
                    used_at=datetime.utcnow(),
                )
                promo.used_count = (promo.used_count or 0) + 1
                db.session.add(usage)

            # 5e. Record RewardTransaction & Credit 2% Cashback to user balance
            if cashback_amount > 0:
                reward_tx = RewardTransaction(
                    user_id=user_id,
                    booking_id=booking.id,
                    transaction_type="cashback_credit",
                    amount=cashback_amount,
                    description=f"2% Cashback reward for booking {booking_ref}",
                    created_at=datetime.utcnow(),
                )
                current_reward = float(user.reward_balance or 0.0)
                user.reward_balance = round(current_reward + cashback_amount, 2)
                db.session.add(reward_tx)

            # 5f. Convert SeatHold records into consumed state
            for hold, _, _ in held_seats:
                hold.status = "consumed"
                db.session.add(hold)

            # 5g. Create unique Ticket for this confirmed booking
            ticket_token = "TKT-" + uuid.uuid4().hex[:16].upper()
            qr_data = f"/verify/{ticket_token}"
            ticket = Ticket(
                booking_id=booking.id,
                ticket_token=ticket_token,
                ticket_status="valid",
                qr_data=qr_data,
                issued_at=datetime.utcnow(),
            )
            db.session.add(ticket)

            # Commit the entire transaction atomically!
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return fail(f"Booking transaction failed: {str(e)}", 500)

        return ok(
            "Booking confirmed successfully",
            {
                "booking_id": booking.id,
                "booking_reference": booking.booking_reference,
                "ticket_token": ticket.ticket_token,
                "event_id": event.id,
                "event_title": event.title,
                "total_amount": float(booking.total_amount),
                "discount_amount": float(booking.discount_amount),
                "cashback_amount": float(booking.cashback_amount),
                "status": booking.status,
                "booked_at": booking.booked_at.isoformat(),
                "seats_count": len(held_seats),
                "addons_count": len(addon_records_to_create),
                "user_reward_balance": float(user.reward_balance),
            },
            status=201,
        )

    # ---------------------------------------------------------------- #
    # READ & LOOKUP
    # ---------------------------------------------------------------- #
    def get_booking_by_id(self, booking_id: int) -> dict:
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)
        return ok("Booking retrieved", booking_to_dict(b))

    def get_booking_by_reference(self, reference: str) -> dict:
        if not reference:
            return fail("Reference is required", 400)
        b = self.booking_dao.get_booking_by_reference(reference)
        if b is None:
            return fail("Booking not found", 404)

        # Enrich with event, items, addons, promo, reward info
        event = self.event_dao.get_event_by_id(b.event_id)
        items = self.booking_item_dao.get_items_by_booking(b.id)
        addons = self.booking_addon_dao.get_addons_by_booking(b.id)

        item_details = []
        for i in items:
            seat_info = self.seat_dao.get_seat_by_id(i.seat_id) if i.seat_id else None
            item_details.append({
                "item_id": i.id,
                "seat_id": i.seat_id,
                "seat_number": seat_info.seat_number if seat_info else "General",
                "unit_price": float(i.unit_price),
                "total_price": float(i.total_price),
            })

        addon_details = []
        for a in addons:
            ad_model = self.event_addon_dao.get_addon_by_id(a.addon_id)
            addon_details.append({
                "addon_id": a.addon_id,
                "name": ad_model.name if ad_model else "Add-on",
                "quantity": a.quantity,
                "unit_price": float(a.unit_price),
                "total_price": float(a.total_price),
            })

        data = booking_to_dict(b)
        data["event_title"] = event.title if event else "Event"
        data["event_date"] = str(event.event_date) if event else ""
        data["start_time"] = str(event.start_time) if event else ""
        data["items"] = item_details
        data["seat_items"] = item_details
        data["addons"] = addon_details

        # Attach ticket_token if ticket exists
        t = self.ticket_dao.get_ticket_by_booking(b.id)
        data["ticket_token"] = t.ticket_token if t else None
        data["ticket_status"] = t.ticket_status if t else None

        return ok("Booking retrieved", data)

    def get_user_bookings(self, user_id: int) -> dict:
        bookings = self.booking_dao.get_user_bookings(user_id)
        result = []
        for b in bookings:
            d = booking_to_dict(b)
            ev = self.event_dao.get_event_by_id(b.event_id)
            d["event_title"] = ev.title if ev else "Event"
            d["event_date"] = str(ev.event_date) if ev else ""
            t = self.ticket_dao.get_ticket_by_booking(b.id)
            d["ticket_token"] = t.ticket_token if t else None
            d["ticket_status"] = t.ticket_status if t else None
            result.append(d)
        return ok("User bookings retrieved", result)

    def cancel_booking(self, booking_id: int) -> dict:
        b = self.booking_dao.get_booking_by_id(booking_id)
        if b is None:
            return fail("Booking not found", 404)
        if b.status == "cancelled":
            return fail("Booking is already cancelled", 409)

        try:
            self.booking_dao.cancel_booking(b)
        except Exception:
            return fail("Could not cancel booking", 500)
        return ok("Booking cancelled", booking_to_dict(b))
