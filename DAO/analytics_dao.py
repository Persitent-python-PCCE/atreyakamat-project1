# DAO/analytics_dao.py
#
# AnalyticsDAO — Data Access Object for Admin Analytics queries.
# Uses explicit, beginner-friendly SQLAlchemy queries on MySQL tables.
#
# Architecture:
#   Controller -> AnalyticsService -> AnalyticsDAO -> MySQL

from datetime import date, datetime, timedelta
from sqlalchemy import func, desc

from app import db
from models.booking import Booking
from models.booking_item import BookingItem
from models.event import Event
from models.category import Category
from models.venue import Venue
from models.user import User
from models.seat import Seat
from models.ticket import Ticket
from models.ticket_verification import TicketVerification
from models.seat_hold import SeatHold
from models.event_reschedule import EventReschedule
from models.promo_code import PromoCode
from models.promo_code_usage import PromoCodeUsage


class AnalyticsDAO:
    """Database aggregation queries for platform analytics."""

    # 1. Total Events & Status Splits
    def get_total_events(self) -> int:
        """Count total events created in the system."""
        return Event.query.count()

    def get_total_published_events(self) -> int:
        """Count published events."""
        return Event.query.filter_by(status="published").count()

    def get_total_unpublished_events(self) -> int:
        """Count unpublished events."""
        return Event.query.filter_by(status="unpublished").count()

    # 2. Active / Upcoming Events
    def get_active_events(self) -> int:
        """Count published events occurring today or in the future."""
        today = date.today()
        return Event.query.filter(
            Event.status == "published",
            Event.event_date >= today,
        ).count()

    # 3. Total Bookings (Confirmed)
    def get_total_bookings(self, start_date: datetime | None = None) -> int:
        """Count total confirmed bookings."""
        query = Booking.query.filter(Booking.status == "confirmed")
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        return query.count()

    # 4. Cancelled Bookings
    def get_cancelled_bookings(self, start_date: datetime | None = None) -> int:
        """Count total cancelled bookings."""
        query = Booking.query.filter(Booking.status == "cancelled")
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        return query.count()

    # 5. Total Revenue
    def get_total_revenue(self, start_date: datetime | None = None) -> float:
        """Sum total paid amount for confirmed bookings."""
        query = db.session.query(func.coalesce(func.sum(Booking.total_amount), 0.0)).filter(
            Booking.status == "confirmed"
        )
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        result = query.scalar()
        return round(float(result or 0.0), 2)

    # 6. Total Cashback Given
    def get_total_cashback(self, start_date: datetime | None = None) -> float:
        """Sum total 2% cashback granted on confirmed bookings."""
        query = db.session.query(func.coalesce(func.sum(Booking.cashback_amount), 0.0)).filter(
            Booking.status == "confirmed"
        )
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        result = query.scalar()
        return round(float(result or 0.0), 2)

    # 7. Total Tickets Sold
    def get_total_tickets_sold(self, start_date: datetime | None = None) -> int:
        """Sum total quantity of tickets sold from confirmed booking items."""
        query = (
            db.session.query(func.coalesce(func.sum(BookingItem.quantity), 0))
            .join(Booking, Booking.id == BookingItem.booking_id)
            .filter(Booking.status == "confirmed")
        )
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        result = query.scalar()
        return int(result or 0)

    # 8. Average Booking Value
    def get_average_booking_value(self, start_date: datetime | None = None) -> float:
        """Compute Average Booking Value (ABV) = Total Revenue / Total Confirmed Bookings."""
        total_rev = self.get_total_revenue(start_date)
        total_bks = self.get_total_bookings(start_date)
        if total_bks == 0:
            return 0.0
        return round(total_rev / total_bks, 2)

    # 9. Top Selling Events
    def get_top_selling_events(self, limit: int = 5, start_date: datetime | None = None) -> list[dict]:
        """Return top events ordered by total revenue from confirmed bookings."""
        events = Event.query.all()
        results = []

        for ev in events:
            # Query confirmed bookings for this event
            bk_query = Booking.query.filter(
                Booking.event_id == ev.id,
                Booking.status == "confirmed",
            )
            if start_date:
                bk_query = bk_query.filter(Booking.booked_at >= start_date)

            confirmed_bookings = bk_query.all()
            booking_count = len(confirmed_bookings)
            total_rev = sum(float(b.total_amount) for b in confirmed_bookings)

            # Tickets sold for this event
            tickets_sold = 0
            for b in confirmed_bookings:
                items = BookingItem.query.filter_by(booking_id=b.id).all()
                tickets_sold += sum(it.quantity or 1 for it in items)

            # Venue and Occupancy
            venue = Venue.query.get(ev.venue_id) if ev.venue_id else None
            venue_capacity = venue.capacity if venue and venue.capacity else 0
            occupancy_rate = self.calculate_event_occupancy(ev.id)

            category = Category.query.get(ev.category_id) if ev.category_id else None

            results.append({
                "event_id": ev.id,
                "title": ev.title,
                "category_name": category.name if category else "General",
                "venue_name": venue.name if venue else "Main Venue",
                "event_date": str(ev.event_date),
                "bookings_count": booking_count,
                "tickets_sold": tickets_sold,
                "revenue": round(total_rev, 2),
                "venue_capacity": venue_capacity,
                "occupancy_rate": occupancy_rate,
                "status": ev.status,
            })

        # Sort by revenue descending, then tickets sold descending
        results.sort(key=lambda x: (x["revenue"], x["tickets_sold"]), reverse=True)
        return results[:limit]

    def calculate_event_occupancy(self, event_id: int) -> float:
        """
        WHY: Occupancy is calculated dynamically based on requires_seats:
        - For seated events: sold seats / total active seats * 100
        - For General Admission events: quantity sold / capacity * 100
        """
        event = Event.query.get(event_id)
        if not event:
            return 0.0

        if event.requires_seats:
            total_seats = Seat.query.filter_by(venue_id=event.venue_id, is_active=True).count()
            if total_seats == 0:
                return 0.0
            sold_seats = db.session.query(func.count(BookingItem.id))\
                .join(Booking, Booking.id == BookingItem.booking_id)\
                .filter(Booking.event_id == event.id, Booking.status == "confirmed", BookingItem.seat_id.isnot(None))\
                .scalar() or 0
            return round((sold_seats / total_seats) * 100.0, 1)
        else:
            capacity = event.venue.capacity if event.venue else 0
            if capacity == 0:
                return 0.0
            sold_qty = db.session.query(func.coalesce(func.sum(BookingItem.quantity), 0))\
                .join(Booking, Booking.id == BookingItem.booking_id)\
                .filter(Booking.event_id == event.id, Booking.status == "confirmed")\
                .scalar() or 0
            return round((int(sold_qty) / capacity) * 100.0, 1)

    def get_total_registered_customers(self) -> int:
        """Count users with customer role."""
        return User.query.filter_by(role="customer").count()

    def get_total_venues(self) -> int:
        """Count total venues."""
        return Venue.query.count()

    def get_tickets_sold_by_type(self, start_date: datetime | None = None) -> dict:
        """Sum seated tickets and GA tickets separately."""
        query_seated = (
            db.session.query(func.coalesce(func.sum(BookingItem.quantity), 0))
            .join(Booking, Booking.id == BookingItem.booking_id)
            .filter(Booking.status == "confirmed", BookingItem.seat_id.isnot(None))
        )
        query_ga = (
            db.session.query(func.coalesce(func.sum(BookingItem.quantity), 0))
            .join(Booking, Booking.id == BookingItem.booking_id)
            .filter(Booking.status == "confirmed", BookingItem.seat_id.is_(None))
        )
        if start_date:
            query_seated = query_seated.filter(Booking.booked_at >= start_date)
            query_ga = query_ga.filter(Booking.booked_at >= start_date)
        return {
            "seated": int(query_seated.scalar() or 0),
            "general_admission": int(query_ga.scalar() or 0),
        }

    # 10. Revenue by Category
    def get_revenue_by_category(self, start_date: datetime | None = None) -> list[dict]:
        """Aggregate total revenue, tickets sold, and bookings count per category."""
        categories = Category.query.all()
        results = []

        for cat in categories:
            # Events in this category
            events = Event.query.filter_by(category_id=cat.id).all()
            event_ids = [e.id for e in events]

            if not event_ids:
                results.append({
                    "category_id": cat.id,
                    "name": cat.name,
                    "bookings_count": 0,
                    "tickets_sold": 0,
                    "revenue": 0.0,
                })
                continue

            # Confirmed bookings for events in this category
            bk_query = Booking.query.filter(
                Booking.event_id.in_(event_ids),
                Booking.status == "confirmed",
            )
            if start_date:
                bk_query = bk_query.filter(Booking.booked_at >= start_date)

            confirmed_bookings = bk_query.all()
            cat_revenue = sum(float(b.total_amount) for b in confirmed_bookings)

            cat_tickets = 0
            for b in confirmed_bookings:
                items = BookingItem.query.filter_by(booking_id=b.id).all()
                cat_tickets += sum(it.quantity or 1 for it in items)

            results.append({
                "category_id": cat.id,
                "name": cat.name,
                "bookings_count": len(confirmed_bookings),
                "tickets_sold": cat_tickets,
                "revenue": round(cat_revenue, 2),
            })

        results.sort(key=lambda x: x["revenue"], reverse=True)
        return results

    # 11. Sales Over Time (Daily aggregation)
    def get_sales_over_time(self, days: int = 30) -> list[dict]:
        """Aggregate daily bookings count, tickets sold, and revenue for the last N days."""
        today = date.today()
        start_date = today - timedelta(days=days - 1)

        # Get all confirmed bookings since start_date
        bookings = (
            Booking.query.filter(
                Booking.status == "confirmed",
                func.date(Booking.booked_at) >= start_date,
            )
            .order_by(Booking.booked_at.asc())
            .all()
        )

        # Build day-by-day mapping
        daily_stats = {}
        for i in range(days):
            current_day = start_date + timedelta(days=i)
            day_str = current_day.strftime("%Y-%m-%d")
            daily_stats[day_str] = {
                "date": day_str,
                "display_date": current_day.strftime("%b %d"),
                "bookings": 0,
                "tickets": 0,
                "revenue": 0.0,
            }

        for b in bookings:
            if b.booked_at:
                day_str = b.booked_at.strftime("%Y-%m-%d")
                if day_str in daily_stats:
                    daily_stats[day_str]["bookings"] += 1
                    daily_stats[day_str]["revenue"] = round(
                        daily_stats[day_str]["revenue"] + float(b.total_amount), 2
                    )
                    items = BookingItem.query.filter_by(booking_id=b.id).all()
                    daily_stats[day_str]["tickets"] += sum(it.quantity or 1 for it in items)

        return list(daily_stats.values())

    # 12. Active Holds & Expired Holds
    def get_active_holds_count(self) -> int:
        """Count currently unexpired active seat holds across all events."""
        now = datetime.utcnow()
        return SeatHold.query.filter(
            SeatHold.status == "active",
            SeatHold.expires_at > now,
        ).count()

    def get_expired_holds_today_count(self) -> int:
        """Count seat holds that expired today."""
        today = date.today()
        return SeatHold.query.filter(
            SeatHold.status == "expired",
            func.date(SeatHold.held_at) == today,
        ).count()

    # 13. Total Checked In Tickets
    def get_total_checked_in_tickets(self, start_date: datetime | None = None) -> int:
        """Count total tickets used/scanned successfully."""
        query = (
            db.session.query(func.count(Ticket.id))
            .join(Booking, Booking.id == Ticket.booking_id)
            .filter(Booking.status == "confirmed", Ticket.ticket_status == "used")
        )
        if start_date:
            query = query.filter(Booking.booked_at >= start_date)
        return int(query.scalar() or 0)

    # 14. Event Operations Summary for a Single Event
    def get_event_operations_summary(self, event_id: int) -> dict | None:
        """Calculate complete real-time operational statistics for a single event."""
        event = Event.query.get(event_id)
        if not event:
            return None

        venue = Venue.query.get(event.venue_id) if event.venue_id else None

        # Calculate event capacity
        if event.requires_seats:
            capacity = Seat.query.filter_by(venue_id=event.venue_id, is_active=True).count()
        else:
            capacity = venue.capacity if venue else 0
        if capacity == 0 and venue and venue.capacity:
            capacity = venue.capacity

        # Confirmed and cancelled bookings
        confirmed_bookings = Booking.query.filter_by(event_id=event.id, status="confirmed").all()
        confirmed_bookings_count = len(confirmed_bookings)
        cancelled_bookings_count = Booking.query.filter_by(event_id=event.id, status="cancelled").count()
        total_bookings_count = confirmed_bookings_count + cancelled_bookings_count

        # Total revenue
        revenue = round(sum(float(b.total_amount) for b in confirmed_bookings), 2)

        # Tickets sold
        if event.requires_seats:
            tickets_sold = (
                db.session.query(func.count(BookingItem.id))
                .join(Booking, Booking.id == BookingItem.booking_id)
                .filter(
                    Booking.event_id == event.id,
                    Booking.status == "confirmed",
                    BookingItem.seat_id.isnot(None),
                )
                .scalar()
                or 0
            )
        else:
            tickets_sold = (
                db.session.query(func.coalesce(func.sum(BookingItem.quantity), 0))
                .join(Booking, Booking.id == BookingItem.booking_id)
                .filter(
                    Booking.event_id == event.id,
                    Booking.status == "confirmed",
                )
                .scalar()
                or 0
            )
        tickets_sold = int(tickets_sold)

        # Checked in tickets
        checked_in = (
            db.session.query(func.count(Ticket.id))
            .join(Booking, Booking.id == Ticket.booking_id)
            .filter(
                Booking.event_id == event.id,
                Booking.status == "confirmed",
                Ticket.ticket_status == "used",
            )
            .scalar()
            or 0
        )
        checked_in = int(checked_in)

        # Remaining capacity
        remaining_capacity = max(0, capacity - tickets_sold)

        # Sales Occupancy %
        sales_occupancy = round((tickets_sold / capacity * 100.0), 1) if capacity > 0 else 0.0

        # Live Occupancy %
        live_occupancy = round((checked_in / capacity * 100.0), 1) if capacity > 0 else 0.0

        # Active holds for this event
        now = datetime.utcnow()
        active_holds = SeatHold.query.filter(
            SeatHold.event_id == event.id,
            SeatHold.status == "active",
            SeatHold.expires_at > now,
        ).count()

        # Expired holds today for this event
        today = date.today()
        expired_holds_today = SeatHold.query.filter(
            SeatHold.event_id == event.id,
            SeatHold.status == "expired",
            func.date(SeatHold.held_at) == today,
        ).count()

        # No-shows = tickets sold - checked in
        no_shows = max(0, tickets_sold - checked_in)
        no_show_rate = round((no_shows / tickets_sold * 100.0), 1) if tickets_sold > 0 else 0.0

        # Last ticket scan timestamp
        last_scan_record = (
            db.session.query(TicketVerification.verified_at)
            .join(Ticket, Ticket.id == TicketVerification.ticket_id)
            .join(Booking, Booking.id == Ticket.booking_id)
            .filter(Booking.event_id == event.id, TicketVerification.verification_status == "success")
            .order_by(desc(TicketVerification.verified_at))
            .first()
        )
        last_scan = last_scan_record[0].strftime("%I:%M %p") if last_scan_record and last_scan_record[0] else None

        # Calculate Health Score
        health = self._compute_event_health_score(
            event=event,
            capacity=capacity,
            tickets_sold=tickets_sold,
            checked_in=checked_in,
            cancelled_count=cancelled_bookings_count,
            total_bookings_count=total_bookings_count,
        )

        # Build Activity Feed (last 10 important actions)
        activity_timeline = self._get_event_activity_timeline(event.id)

        return {
            "event_id": event.id,
            "title": event.title,
            "status": event.status,
            "event_date": event.event_date.isoformat() if event.event_date else None,
            "start_time": str(event.start_time) if event.start_time else None,
            "venue_name": venue.name if venue else "Unknown Venue",
            "venue_type": venue.venue_type if venue else ("seated" if event.requires_seats else "general"),
            "requires_seats": event.requires_seats,
            "booking_open": event.booking_open,
            "poster": event.poster,
            "capacity": capacity,
            "tickets_sold": tickets_sold,
            "checked_in": checked_in,
            "remaining_capacity": remaining_capacity,
            "sales_occupancy": sales_occupancy,
            "live_occupancy": live_occupancy,
            "active_holds": active_holds,
            "expired_holds_today": expired_holds_today,
            "cancellations": cancelled_bookings_count,
            "no_shows": no_shows,
            "no_show_rate": no_show_rate,
            "last_scan": last_scan,
            "revenue": revenue,
            "health_score": health["score"],
            "health_category": health["category"],
            "health_reasons": health["reasons"],
            "timeline": activity_timeline,
        }

    # Helper: Health score computation
    def _compute_event_health_score(
        self, event: Event, capacity: int, tickets_sold: int, checked_in: int, cancelled_count: int, total_bookings_count: int
    ) -> dict:
        """Transparent, rule-based 0-100 Event Health Score computation."""
        # 1. Sales Occupancy Factor (0 to 40 pts)
        sales_occ = (tickets_sold / capacity * 100.0) if capacity > 0 else 0.0
        sales_score = min(40.0, (sales_occ / 100.0) * 40.0)

        # 2. Cancellation Factor (0 to 20 pts)
        tot_bk = total_bookings_count if total_bookings_count > 0 else (tickets_sold + cancelled_count)
        cancellation_rate = (cancelled_count / tot_bk) if tot_bk > 0 else 0.0
        cancel_score = max(0.0, 20.0 - (cancellation_rate * 40.0))

        # 3. Timing & Velocity Factor (0 to 20 pts)
        days_to_event = (event.event_date - date.today()).days if event.event_date else 0
        if days_to_event > 14:
            timing_score = 20.0 if sales_occ >= 20.0 else 15.0
        elif days_to_event >= 0:
            timing_score = 20.0 if sales_occ >= 50.0 else (10.0 + (sales_occ / 10.0))
        else:
            timing_score = 20.0 if sales_occ >= 60.0 else 12.0
        timing_score = min(20.0, timing_score)

        # 4. Live Attendance Factor (0 to 20 pts)
        if days_to_event <= 0:
            att_rate = (checked_in / tickets_sold) if tickets_sold > 0 else 0.0
            attendance_score = att_rate * 20.0
        else:
            attendance_score = 20.0
        attendance_score = min(20.0, attendance_score)

        total_score = round(min(100.0, max(0.0, sales_score + cancel_score + timing_score + attendance_score)))

        if total_score >= 80:
            category = "Excellent"
        elif total_score >= 60:
            category = "Healthy"
        elif total_score >= 40:
            category = "Needs Attention"
        else:
            category = "At Risk"

        reasons = []
        reasons.append(f"{round(sales_occ, 1)}% sales occupancy ({tickets_sold}/{capacity} tickets sold)")
        if cancellation_rate > 0.15:
            reasons.append(f"Elevated cancellation rate ({round(cancellation_rate * 100, 1)}%)")
        else:
            reasons.append(f"Low cancellation rate ({round(cancellation_rate * 100, 1)}%)")

        if days_to_event <= 0:
            live_occ = (checked_in / capacity * 100.0) if capacity > 0 else 0.0
            reasons.append(f"{round(live_occ, 1)}% live attendance ({checked_in} checked in)")
        else:
            reasons.append(f"Scheduled in {days_to_event} days")

        return {
            "score": int(total_score),
            "category": category,
            "reasons": reasons,
        }

    # Helper: Activity timeline
    def _get_event_activity_timeline(self, event_id: int) -> list[dict]:
        """Aggregate recent business operations into an activity timeline."""
        timeline = []

        # Recent ticket scans
        scans = (
            db.session.query(TicketVerification, Ticket)
            .join(Ticket, Ticket.id == TicketVerification.ticket_id)
            .join(Booking, Booking.id == Ticket.booking_id)
            .filter(Booking.event_id == event_id)
            .order_by(desc(TicketVerification.verified_at))
            .limit(5)
            .all()
        )
        for ver, tkt in scans:
            timeline.append({
                "time": ver.verified_at.strftime("%I:%M %p") if ver.verified_at else "",
                "timestamp": ver.verified_at or datetime.utcnow(),
                "action": "Ticket verified" if ver.verification_status == "success" else "Ticket scan failed",
                "details": f"Token {tkt.ticket_token} ({ver.verification_status})",
                "type": "scan",
            })

        # Recent bookings
        bookings = (
            Booking.query.filter_by(event_id=event_id)
            .order_by(desc(Booking.booked_at))
            .limit(5)
            .all()
        )
        for b in bookings:
            timeline.append({
                "time": b.booked_at.strftime("%I:%M %p") if b.booked_at else "",
                "timestamp": b.booked_at or datetime.utcnow(),
                "action": "Booking created" if b.status == "confirmed" else f"Booking {b.status}",
                "details": f"Ref {b.booking_reference} · ₹{float(b.total_amount):.2f}",
                "type": "booking",
            })

        # Reschedule history
        reschedules = (
            EventReschedule.query.filter_by(event_id=event_id)
            .order_by(desc(EventReschedule.rescheduled_at))
            .limit(3)
            .all()
        )
        for r in reschedules:
            timeline.append({
                "time": r.rescheduled_at.strftime("%I:%M %p") if r.rescheduled_at else "",
                "timestamp": r.rescheduled_at or datetime.utcnow(),
                "action": "Event rescheduled",
                "details": f"Moved from {r.old_event_date} to {r.new_event_date}",
                "type": "reschedule",
            })

        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline[:10]
