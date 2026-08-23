# Services/email_service.py
#
# EmailService — Handles outbound email delivery via Gmail SMTP with PDF attachment
# and logs every attempt to the `email_logs` table via EmailLogDAO.
#
# Architecture:
#   Controller -> EmailService -> TicketPDFService / EmailLogDAO / BookingDAO -> MySQL

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

from DAO import EmailLogDAO, BookingDAO, UserDAO, EventDAO, VenueDAO, TicketDAO
from models.email_log import EmailLog
from Services.pdf_service import TicketPDFService
from Services._result import ok, fail


class EmailService:
    """Service for sending emails via Gmail SMTP and recording audit logs."""

    def __init__(self):
        self.email_log_dao = EmailLogDAO()
        self.booking_dao = BookingDAO()
        self.user_dao = UserDAO()
        self.event_dao = EventDAO()
        self.venue_dao = VenueDAO()
        self.ticket_dao = TicketDAO()
        self.pdf_service = TicketPDFService()

    def _get_smtp_credentials(self):
        """Load Gmail SMTP configuration strictly from environment variables."""
        gmail_address = os.getenv("GMAIL_ADDRESS", "").strip()
        gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        return gmail_address, gmail_app_password, smtp_host, smtp_port

    def send_booking_confirmation(self, booking_id: int) -> dict:
        """Generate PDF ticket, construct branded email, send via Gmail SMTP, and log audit row."""
        # 1. Load details
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            return fail("Booking not found", 404)

        user = self.user_dao.get_user_by_id(booking.user_id)
        if not user or not user.email:
            return fail("Customer email not found", 404)

        event = self.event_dao.get_event_by_id(booking.event_id)
        venue = self.venue_dao.get_venue_by_id(event.venue_id) if event and event.venue_id else None
        ticket = self.ticket_dao.get_ticket_by_booking(booking.id)

        recipient_email = user.email.strip()
        subject = f"SeatMeUp — Booking Confirmation {booking.booking_reference}"
        email_type = "booking_confirmation"

        # 2. Check SMTP credentials
        gmail_address, gmail_app_password, smtp_host, smtp_port = self._get_smtp_credentials()
        if not gmail_address or not gmail_app_password:
            # Log failure in EmailLog
            log = EmailLog(
                user_id=booking.user_id,
                booking_id=booking.id,
                recipient_email=recipient_email,
                subject=subject,
                email_type=email_type,
                status="failed",
                error_message="Gmail credentials not configured in environment (GMAIL_ADDRESS or GMAIL_APP_PASSWORD missing).",
                created_at=datetime.utcnow(),
            )
            self.email_log_dao.create_log(log)
            return fail("Gmail credentials not configured in environment.", 503)

        # 3. Generate PDF Ticket
        pdf_bytes = self.pdf_service.generate_ticket_pdf(booking.id)

        # 4. Build Email Message
        msg = MIMEMultipart("mixed")
        msg["From"] = f"SeatMeUp <{gmail_address}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Plain text & HTML body
        event_title = event.title if event else "Your Event"
        event_date_str = str(event.event_date) if event else ""
        event_time_str = str(event.start_time) if event else ""
        venue_str = venue.name if venue else "Main Venue"
        paid_str = f"${float(booking.total_amount):.2f}"
        cashback_str = f"${float(booking.cashback_amount or 0.0):.2f}"
        token_str = ticket.ticket_token if ticket else "N/A"

        text_content = f"""Hello {user.name},

Thank you for booking with SeatMeUp! Your order has been confirmed.

Booking Reference: {booking.booking_reference}
Event: {event_title}
Date & Time: {event_date_str} at {event_time_str}
Venue: {venue_str}
Total Paid: {paid_str}
2% Cashback Earned: {cashback_str} (Credited to your reward wallet)
Ticket Token: {token_str}

Your official digital ticket is attached as a PDF. Please present the QR code on your mobile device or print it clearly at the venue entrance.

Enjoy the event!
The SeatMeUp Team
"""

        html_content = f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; margin: 0; padding: 20px; background-color: #f7f7f7;">
  <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
    <div style="background-color: #490E13; padding: 24px; text-align: center; color: #ffffff;">
      <h1 style="margin: 0; font-size: 24px; color: #F54828;">🎟️ SeatMeUp</h1>
      <p style="margin: 5px 0 0 0; font-size: 14px; color: #ffffff;">Booking Confirmed</p>
    </div>
    
    <div style="padding: 24px;">
      <p style="font-size: 16px; margin-top: 0;">Hello <strong>{user.name}</strong>,</p>
      <p>Your booking for <strong>{event_title}</strong> has been successfully confirmed!</p>
      
      <div style="background-color: #fafaf8; border: 1px solid #e5e5e0; border-radius: 8px; padding: 16px; margin: 20px 0;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <tr>
            <td style="padding: 6px 0; color: #666;">Booking Ref:</td>
            <td style="padding: 6px 0; font-weight: bold; text-align: right;">{booking.booking_reference}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #666;">Date &amp; Time:</td>
            <td style="padding: 6px 0; font-weight: bold; text-align: right;">{event_date_str} • {event_time_str}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #666;">Venue:</td>
            <td style="padding: 6px 0; font-weight: bold; text-align: right;">{venue_str}</td>
          </tr>
          <tr style="border-top: 1px solid #e0e0e0;">
            <td style="padding: 8px 0; color: #666;">Total Paid:</td>
            <td style="padding: 8px 0; font-weight: bold; text-align: right; color: #F54828;">{paid_str}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: #28a745;">2% Cashback Earned:</td>
            <td style="padding: 6px 0; font-weight: bold; text-align: right; color: #28a745;">+{cashback_str}</td>
          </tr>
        </table>
      </div>

      <div style="background-color: #fff4f2; border: 1px dashed #F54828; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
        <p style="margin: 0; font-size: 13px; color: #490E13;">
          📎 <strong>Digital Ticket Attached:</strong> Your official PDF ticket containing the admission QR Code is attached to this email.
        </p>
      </div>

      <p style="font-size: 13px; color: #777777; margin-bottom: 0;">
        Present the attached PDF on your phone or print it out at the entrance.<br/>
        We hope you enjoy the experience!
      </p>
    </div>

    <div style="background-color: #f0f0f0; padding: 12px 24px; text-align: center; font-size: 12px; color: #888888;">
      © SeatMeUp • Smart Event Ticketing Platform
    </div>
  </div>
</body>
</html>
"""

        msg_body = MIMEMultipart("alternative")
        msg_body.attach(MIMEText(text_content, "plain"))
        msg_body.attach(MIMEText(html_content, "html"))
        msg.attach(msg_body)

        # 5. Attach PDF if generated
        if pdf_bytes:
            pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
            pdf_filename = f"SeatMeUp-Ticket-{booking.booking_reference}.pdf"
            pdf_attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
            msg.attach(pdf_attachment)

        # 6. Send via Gmail SMTP
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(gmail_address, gmail_app_password)
                server.sendmail(gmail_address, [recipient_email], msg.as_string())

            # Log Success
            sent_time = datetime.utcnow()
            log = EmailLog(
                user_id=booking.user_id,
                booking_id=booking.id,
                recipient_email=recipient_email,
                subject=subject,
                email_type=email_type,
                status="sent",
                error_message=None,
                sent_at=sent_time,
                created_at=sent_time,
            )
            self.email_log_dao.create_log(log)
            return ok("Booking confirmation email sent successfully.", {"email_log_id": log.id, "recipient": recipient_email})

        except Exception as e:
            err_msg = str(e)
            # Ensure sensitive credentials are never leaked in log
            if gmail_app_password:
                err_msg = err_msg.replace(gmail_app_password, "******")

            # Log Failure in EmailLog
            log = EmailLog(
                user_id=booking.user_id,
                booking_id=booking.id,
                recipient_email=recipient_email,
                subject=subject,
                email_type=email_type,
                status="failed",
                error_message=f"SMTP Delivery failed: {err_msg[:400]}",
                sent_at=None,
                created_at=datetime.utcnow(),
            )
            self.email_log_dao.create_log(log)
            return fail(f"Email delivery failed: {err_msg}", 500)

    def resend_booking_confirmation(self, booking_id: int, user_id: int | None = None, is_admin: bool = False) -> dict:
        """Allow booking owner or admin to trigger a confirmation email resend."""
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            return fail("Booking not found", 404)

        if user_id is not None and not is_admin:
            if booking.user_id != user_id:
                return fail("You do not have permission to resend email for this booking", 403)

        return self.send_booking_confirmation(booking.id)
