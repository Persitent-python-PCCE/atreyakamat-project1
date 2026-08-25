# Services/analytics_service.py
#
# AnalyticsService — Orchestrates platform metrics, sales velocity,
# category breakdowns, and revenue statistics for the Admin Dashboard.
#
# Architecture:
#   Controller -> AnalyticsService -> AnalyticsDAO -> MySQL

from datetime import datetime, timedelta
from DAO.analytics_dao import AnalyticsDAO
from Services._result import ok, fail


class AnalyticsService:
    """Service handling business metrics and aggregated platform analytics."""

    def __init__(self):
        self.analytics_dao = AnalyticsDAO()

    def _get_start_date_from_days(self, days: int | None = None) -> datetime | None:
        """Convert a days filter (e.g. 7 or 30) into a cutoff datetime."""
        if not days or days <= 0:
            return None
        return datetime.utcnow() - timedelta(days=days)

    def get_dashboard_summary(self, days: int | None = None) -> dict:
        """Retrieve core platform headline metrics."""
        start_date = self._get_start_date_from_days(days)

        total_events = self.analytics_dao.get_total_events()
        upcoming_events = self.analytics_dao.get_active_events() # published, event_date >= today
        active_events = upcoming_events # mapping compatibility
        
        total_bookings = self.analytics_dao.get_total_bookings(start_date)
        confirmed_bookings = total_bookings
        cancelled_bookings = self.analytics_dao.get_cancelled_bookings(start_date)
        
        total_revenue = self.analytics_dao.get_total_revenue(start_date)
        cashback_given = self.analytics_dao.get_total_cashback(start_date)
        tickets_sold = self.analytics_dao.get_total_tickets_sold(start_date)
        average_booking_value = self.analytics_dao.get_average_booking_value(start_date)

        # Event status counts
        published_events = self.analytics_dao.get_total_published_events()
        unpublished_events = self.analytics_dao.get_total_unpublished_events()

        # Operational & Attendance Metrics
        total_registered_customers = self.analytics_dao.get_total_registered_customers()
        total_venues = self.analytics_dao.get_total_venues()
        
        checked_in_tickets = self.analytics_dao.get_total_checked_in_tickets(start_date)
        total_no_shows = max(0, tickets_sold - checked_in_tickets)
        no_show_rate = round((total_no_shows / tickets_sold * 100.0), 1) if tickets_sold > 0 else 0.0

        active_holds = self.analytics_dao.get_active_holds_count()
        expired_holds_today = self.analytics_dao.get_expired_holds_today_count()

        tickets_by_type = self.analytics_dao.get_tickets_sold_by_type(start_date)
        seated_tickets_sold = tickets_by_type["seated"]
        general_admission_sold = tickets_by_type["general_admission"]

        return {
            "total_events": total_events,
            "published_events": published_events,
            "unpublished_events": unpublished_events,
            "upcoming_events": upcoming_events,
            "active_events": active_events,
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue,
            "cashback_given": cashback_given,
            "tickets_sold": tickets_sold,
            "checked_in_tickets": checked_in_tickets,
            "total_no_shows": total_no_shows,
            "no_show_rate": no_show_rate,
            "active_holds": active_holds,
            "expired_holds_today": expired_holds_today,
            "average_booking_value": average_booking_value,
            "total_registered_customers": total_registered_customers,
            "total_venues": total_venues,
            "seated_tickets_sold": seated_tickets_sold,
            "general_admission_sold": general_admission_sold,
        }

    def get_event_operations(self, event_id: int) -> dict:
        """Retrieve full real-time operational dashboard for a specific event."""
        data = self.analytics_dao.get_event_operations_summary(event_id)
        if not data:
            return fail("Event not found", 404)
        return ok("Event operations data retrieved successfully", data)

    def get_top_events(self, limit: int = 5, days: int | None = None) -> list[dict]:
        """Retrieve top performing events by revenue and ticket volume."""
        start_date = self._get_start_date_from_days(days)
        return self.analytics_dao.get_top_selling_events(limit=limit, start_date=start_date)

    def get_category_performance(self, days: int | None = None) -> list[dict]:
        """Retrieve category revenue and volume breakdowns."""
        start_date = self._get_start_date_from_days(days)
        return self.analytics_dao.get_revenue_by_category(start_date)

    def get_sales_over_time(self, days: int = 30) -> list[dict]:
        """Retrieve daily sales progression over the given day horizon."""
        return self.analytics_dao.get_sales_over_time(days=days or 30)

    def get_full_analytics(self, days: int | None = None) -> dict:
        """
        WHY: Analytics are cached for 60 seconds because they are read-heavy
        and do not need second-by-second freshness.
        """
        from app import cache
        cache_key = f"full_analytics_{days or 'all'}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return ok("Analytics retrieved successfully (cached)", cached_data)

        summary = self.get_dashboard_summary(days=days)
        top_events = self.get_top_events(limit=5, days=days)
        revenue_by_category = self.get_category_performance(days=days)
        trend_days = days if days and days > 0 else 30
        sales_over_time = self.get_sales_over_time(days=trend_days)

        data = {
            "summary": summary,
            "top_events": top_events,
            "revenue_by_category": revenue_by_category,
            "sales_over_time": sales_over_time,
            "filter_days": days,
        }

        # Cache the result for 60 seconds
        cache.set(cache_key, data, timeout=60)

        return ok("Analytics retrieved successfully", data)
