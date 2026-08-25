# tests/integration/test_mysql_schema.py
#
# LAYER 3: MySQL Compatibility & Schema Smoke Test.
#
# WHY THIS TEST EXISTS:
#   Catches MySQL-specific ENUM and column truncation regressions (such as 'expired' / 'consumed'
#   in seat_holds.status or 'published' in events.status) without destructive DDL.
#
# RULES:
#   - NEVER run db.drop_all() or db.create_all() here.
#   - Only executed when SEATMEUP_RUN_MYSQL_TESTS=1 is set.
#   - Uses read-only SHOW COLUMNS inspection.

import os
import pytest
from sqlalchemy import create_engine, text
from Config.config import DevelopmentConfig


@pytest.mark.mysql
class TestMySQLSchemaCompatibility:
    @pytest.fixture(autouse=True)
    def setup_mysql_engine(self):
        if os.getenv("SEATMEUP_RUN_MYSQL_TESTS") != "1":
            pytest.skip("Skipping live MySQL test (set SEATMEUP_RUN_MYSQL_TESTS=1 to run)")

        self.engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
        yield
        self.engine.dispose()

    def test_mysql_seat_holds_status_enum_contains_expired_and_consumed(self):
        """WHY: Real MySQL seat_holds table must permit 'active', 'expired', and 'consumed' without 1265 truncation."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM seat_holds LIKE 'status'")).fetchone()
            assert result is not None
            col_type = result[1].lower()
            assert "expired" in col_type
            assert "consumed" in col_type
            assert "active" in col_type

    def test_mysql_events_status_enum_contains_published(self):
        """WHY: Real MySQL events table must permit ONLY 'published' and 'unpublished'."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM events LIKE 'status'")).fetchone()
            assert result is not None
            col_type = result[1].lower()
            assert "published" in col_type
            assert "unpublished" in col_type
            assert "draft" not in col_type
            assert "cancelled" not in col_type
            assert "completed" not in col_type

    def test_mysql_venues_venue_type_enum_contains_general(self):
        """WHY: Real MySQL venues table must permit both 'seated' and 'general' venue types."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM venues LIKE 'venue_type'")).fetchone()
            assert result is not None
            col_type = result[1].lower()
            assert "general" in col_type
            assert "seated" in col_type
