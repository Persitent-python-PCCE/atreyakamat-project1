# DAO/analytics_dao.py
#
# AnalyticsDAO — Data Access Object for Admin Analytics queries.
# Uses explicit, beginner-friendly SQLAlchemy queries on MySQL tables.
#
# Architecture:
#   Controller -> AnalyticsService -> AnalyticsDAO -> MySQL

from datetime import date, datetime, timedelta
from sqlalchemy import func

from app import db
from models.booking import Booking
from models.booking_item import BookingItem
from models.event import Event
from models.category import Category
from models.venue import Venue
from models.user import User


class AnalyticsDAO:
    """Database aggregation queries for platform analytics."""

    # 1. Total Events
    def get_total_events(self) -> int:
        """Count total events created in the system."""
        return Event.query.count()

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
            occupancy_rate = 0.0
            if venue_capacity > 0:
                occupancy_rate = round((tickets_sold / venue_capacity) * 100.0, 1)

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
