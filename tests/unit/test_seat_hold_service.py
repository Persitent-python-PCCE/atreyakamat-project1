# tests/unit/test_seat_hold_service.py
#
# Pure unit tests for SeatHoldService with mocked SeatHoldDAO.
# WHY: Verifies low-level seat hold token querying and deletion.

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone
from Services.seat_hold_service import SeatHoldService
from models.seat_hold import SeatHold


@pytest.mark.unit
class TestSeatHoldService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.hold_service = SeatHoldService()
        self.mock_dao = MagicMock()
        self.mock_event_dao = MagicMock()
        self.mock_seat_dao = MagicMock()

        self.hold_service.hold_dao = self.mock_dao
        self.hold_service.event_dao = self.mock_event_dao
        self.hold_service.seat_dao = self.mock_seat_dao

    def test_get_hold_by_token_found(self):
        """WHY: Valid hold token lookup returns serialized seat hold."""
        fake_hold = SeatHold(
            id=1,
            hold_token="TOK-12345",
            event_id=1,
            seat_id=10,
            user_id=2,
            status="active",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
        )
        self.mock_dao.get_hold_by_token.return_value = fake_hold

        res = self.hold_service.get_hold_by_token("TOK-12345")
        assert res["success"] is True
        assert res["data"]["hold_token"] == "TOK-12345"

    def test_get_hold_by_token_not_found(self):
        """WHY: Non-existent hold token returns 404."""
        self.mock_dao.get_hold_by_token.return_value = None
        res = self.hold_service.get_hold_by_token("NONEXISTENT")
        assert res["success"] is False
        assert res["status"] == 404

    def test_delete_hold(self):
        """WHY: Hold deletion delegating to DAO correctly removes row."""
        fake_hold = SeatHold(id=2)
        self.mock_dao.get_hold_by_id.return_value = fake_hold

        res = self.hold_service.delete_hold(2)
        assert res["success"] is True
        self.mock_dao.delete_hold.assert_called_once_with(fake_hold)
