# tests/unit/test_analytics_service.py
#
# Pure unit tests for AnalyticsService with mocked AnalyticsDAO.
# WHY: Verifies business metric aggregation (revenue, tickets, occupancy, category breakdown)
# used by executive and admin dashboard reports.

import pytest
from unittest.mock import MagicMock, patch
from Services.analytics_service import AnalyticsService


@pytest.mark.unit
class TestAnalyticsService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.analytics_service = AnalyticsService()
        self.mock_dao = MagicMock()
        self.mock_dao.get_total_events.return_value = 0
        self.mock_dao.get_active_events.return_value = 0
        self.mock_dao.get_total_published_events.return_value = 0
        self.mock_dao.get_total_unpublished_events.return_value = 0
        self.mock_dao.get_total_bookings.return_value = 0
        self.mock_dao.get_cancelled_bookings.return_value = 0
        self.mock_dao.get_total_revenue.return_value = 0.0
        self.mock_dao.get_total_cashback.return_value = 0.0
        self.mock_dao.get_total_tickets_sold.return_value = 0
        self.mock_dao.get_average_booking_value.return_value = 0.0
        self.mock_dao.get_total_registered_customers.return_value = 0
        self.mock_dao.get_total_venues.return_value = 0
        self.mock_dao.get_total_checked_in_tickets.return_value = 0
        self.mock_dao.get_active_holds_count.return_value = 0
        self.mock_dao.get_expired_holds_today_count.return_value = 0
        self.mock_dao.get_tickets_sold_by_type.return_value = {"seated": 0, "general_admission": 0}
        self.analytics_service.analytics_dao = self.mock_dao

    def test_get_dashboard_summary(self):
        """WHY: Headline metric aggregation correctly compiles booking, revenue, and ticket statistics."""
        self.mock_dao.get_total_events.return_value = 15
        self.mock_dao.get_active_events.return_value = 10
        self.mock_dao.get_total_bookings.return_value = 120
        self.mock_dao.get_cancelled_bookings.return_value = 5
        self.mock_dao.get_total_revenue.return_value = 12500.00
        self.mock_dao.get_total_cashback.return_value = 250.00
        self.mock_dao.get_total_tickets_sold.return_value = 350
        self.mock_dao.get_average_booking_value.return_value = 104.16

        res = self.analytics_service.get_dashboard_summary(days=30)
        assert res["total_events"] == 15
        assert res["total_revenue"] == 12500.00
        assert res["cashback_given"] == 250.00

    def test_get_full_analytics(self):
        """WHY: Full dashboard analytics payload contains summary, top events, and category breakdowns."""
        self.mock_dao.get_total_events.return_value = 5
        self.mock_dao.get_active_events.return_value = 4
        self.mock_dao.get_total_bookings.return_value = 20
        self.mock_dao.get_cancelled_bookings.return_value = 1
        self.mock_dao.get_total_revenue.return_value = 2000.00
        self.mock_dao.get_total_cashback.return_value = 40.00
        self.mock_dao.get_total_tickets_sold.return_value = 30
        self.mock_dao.get_average_booking_value.return_value = 100.00

        self.mock_dao.get_top_selling_events.return_value = [{"event_id": 1, "title": "Concert", "tickets_sold": 30}]
        self.mock_dao.get_revenue_by_category.return_value = [{"category_name": "Music", "total_revenue": 2000.00}]
        self.mock_dao.get_sales_over_time.return_value = [{"date": "2026-08-20", "revenue": 500.00}]

        res = self.analytics_service.get_full_analytics(days=30)
        assert res["success"] is True
        assert "summary" in res["data"]
        assert "top_events" in res["data"]
        assert "revenue_by_category" in res["data"]
        assert "sales_over_time" in res["data"]

    @patch("flask_caching.Cache.get")
    @patch("flask_caching.Cache.set")
    def test_caching_behavior(self, mock_set, mock_get):
        """WHY: Verifies that full analytics queries the cache and sets a new value on miss."""
        mock_get.return_value = None  # Cache miss

        self.mock_dao.get_total_events.return_value = 5
        self.mock_dao.get_active_events.return_value = 4
        self.mock_dao.get_total_bookings.return_value = 20
        self.mock_dao.get_cancelled_bookings.return_value = 1
        self.mock_dao.get_total_revenue.return_value = 2000.00
        self.mock_dao.get_total_cashback.return_value = 40.00
        self.mock_dao.get_total_tickets_sold.return_value = 30
        self.mock_dao.get_average_booking_value.return_value = 100.00
        self.mock_dao.get_tickets_sold_by_type.return_value = {"seated": 10, "general_admission": 20}
        self.mock_dao.get_total_registered_customers.return_value = 50
        self.mock_dao.get_total_venues.return_value = 2

        self.mock_dao.get_top_selling_events.return_value = []
        self.mock_dao.get_revenue_by_category.return_value = []
        self.mock_dao.get_sales_over_time.return_value = []

        res = self.analytics_service.get_full_analytics(days=30)
        assert res["success"] is True
        mock_get.assert_called_once()
        mock_set.assert_called_once()
