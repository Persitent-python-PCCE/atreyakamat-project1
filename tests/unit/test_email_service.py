# tests/unit/test_email_service.py
#
# Pure unit tests for EmailService with mocked SMTP client and DAO calls.
# WHY: External email servers (Gmail SMTP) must be strictly mocked to:
#   1. Prevent actual emails being sent to test/dummy addresses.
#   2. Avoid network latency and flaky test suite execution.
#   3. Test graceful failure logging in `email_logs` when SMTP encounters connection errors.

import pytest
from unittest.mock import patch, MagicMock
from Services.email_service import EmailService
from models.booking import Booking
from models.user import User
from models.event import Event
from models.venue import Venue
from models.ticket import Ticket


@pytest.mark.unit
class TestEmailService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.email_service = EmailService()
        self.mock_booking_dao = MagicMock()
        self.mock_user_dao = MagicMock()
        self.mock_event_dao = MagicMock()
        self.mock_venue_dao = MagicMock()
        self.mock_ticket_dao = MagicMock()
        self.mock_log_dao = MagicMock()
        self.mock_pdf_service = MagicMock()

        self.email_service.booking_dao = self.mock_booking_dao
        self.email_service.user_dao = self.mock_user_dao
        self.email_service.event_dao = self.mock_event_dao
        self.email_service.venue_dao = self.mock_venue_dao
        self.email_service.ticket_dao = self.mock_ticket_dao
        self.email_service.email_log_dao = self.mock_log_dao
        self.email_service.pdf_service = self.mock_pdf_service

    @patch("smtplib.SMTP")
    def test_send_booking_confirmation_success(self, mock_smtp_cls):
        """WHY: Successful SMTP dispatch attaches PDF ticket and logs sent status in EmailLog."""
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        self.mock_booking_dao.get_booking_by_id.return_value = Booking(id=1, user_id=2, event_id=3, booking_reference="SMU-123", total_amount=100.0)
        self.mock_user_dao.get_user_by_id.return_value = User(id=2, name="Alice", email="alice@test.com")
        self.mock_event_dao.get_event_by_id.return_value = Event(id=3, title="Gala", venue_id=4)
        self.mock_venue_dao.get_venue_by_id.return_value = Venue(id=4, name="Grand Hall")
        self.mock_ticket_dao.get_ticket_by_booking.return_value = Ticket(id=5, ticket_token="TKT-123")
        self.mock_pdf_service.generate_ticket_pdf.return_value = b"%PDF-1.4 Fake PDF Bytes"

        with patch.object(self.email_service, "_get_smtp_credentials", return_value=("bot@test.com", "app_pass", "smtp.test.com", 587)):
            res = self.email_service.send_booking_confirmation(1)

        assert res["success"] is True
        assert res["status"] == 200
        self.mock_log_dao.create_log.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_booking_confirmation_smtp_failure_handled_gracefully(self, mock_smtp_cls):
        """WHY: SMTP connection drop or authentication error is captured safely without crashing the request."""
        mock_smtp_cls.side_effect = Exception("SMTP Connection Refused")

        self.mock_booking_dao.get_booking_by_id.return_value = Booking(id=1, user_id=2, event_id=3, booking_reference="SMU-123", total_amount=100.0)
        self.mock_user_dao.get_user_by_id.return_value = User(id=2, name="Alice", email="alice@test.com")
        self.mock_event_dao.get_event_by_id.return_value = Event(id=3, title="Gala", venue_id=4)
        self.mock_venue_dao.get_venue_by_id.return_value = Venue(id=4, name="Grand Hall")
        self.mock_ticket_dao.get_ticket_by_booking.return_value = Ticket(id=5, ticket_token="TKT-123")
        self.mock_pdf_service.generate_ticket_pdf.return_value = b"%PDF-1.4 Fake PDF Bytes"

        with patch.object(self.email_service, "_get_smtp_credentials", return_value=("bot@test.com", "app_pass", "smtp.test.com", 587)):
            res = self.email_service.send_booking_confirmation(1)

        assert res["success"] is False
        assert res["status"] == 500
        assert "failed" in res["message"].lower()
