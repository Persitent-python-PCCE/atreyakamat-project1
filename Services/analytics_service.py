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
        active_events = self.analytics_dao.get_active_events()
        total_bookings = self.analytics_dao.get_total_bookings(start_date)
        cancelled_bookings = self.analytics_dao.get_cancelled_bookings(start_date)
        total_revenue = self.analytics_dao.get_total_revenue(start_date)
        cashback_given = self.analytics_dao.get_total_cashback(start_date)
        tickets_sold = self.analytics_dao.get_total_tickets_sold(start_date)
        average_booking_value = self.analytics_dao.get_average_booking_value(start_date)

        return {
            "total_events": total_events,
            "active_events": active_events,
            "total_bookings": total_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue,
            "cashback_given": cashback_given,
            "tickets_sold": tickets_sold,
            "average_booking_value": average_booking_value,
        }

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
        """Retrieve complete unified analytics payload for web dashboard and REST API."""
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

        return ok("Analytics retrieved successfully", data)
