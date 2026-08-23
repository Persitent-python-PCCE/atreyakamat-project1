# Services/pdf_service.py
#
# TicketPDFService — Generates clean, professional digital ticket PDFs
# using ReportLab and embedded QR codes.
#
# Architecture:
#   Controller -> TicketPDFService -> BookingDAO / TicketDAO / EventDAO / UserDAO -> MySQL

import io
from datetime import datetime
import qrcode
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    HRFlowable,
)

from DAO import (
    BookingDAO,
    TicketDAO,
    EventDAO,
    VenueDAO,
    CategoryDAO,
    UserDAO,
    BookingItemDAO,
    BookingAddonDAO,
    EventAddonDAO,
    SeatDAO,
)


class TicketPDFService:
    """Service to generate branded SeatMeUp PDF tickets."""

    def __init__(self):
        self.booking_dao = BookingDAO()
        self.ticket_dao = TicketDAO()
        self.event_dao = EventDAO()
        self.venue_dao = VenueDAO()
        self.category_dao = CategoryDAO()
        self.user_dao = UserDAO()
        self.booking_item_dao = BookingItemDAO()
        self.booking_addon_dao = BookingAddonDAO()
        self.event_addon_dao = EventAddonDAO()
        self.seat_dao = SeatDAO()

    def generate_ticket_pdf(self, booking_id: int) -> bytes | None:
        """Build and return binary PDF data for a confirmed booking."""
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            return None

        ticket = self.ticket_dao.get_ticket_by_booking(booking.id)
        if not ticket:
            return None

        event = self.event_dao.get_event_by_id(booking.event_id)
        user = self.user_dao.get_user_by_id(booking.user_id)
        venue = self.venue_dao.get_venue_by_id(event.venue_id) if event and event.venue_id else None
        category = self.category_dao.get_category_by_id(event.category_id) if event and event.category_id else None

        # Seats / Items
        items = self.booking_item_dao.get_items_by_booking(booking.id)
        seat_names = []
        ga_quantity = 0
        is_seated = bool(event.requires_seats) if event else True

        for it in items:
            if it.seat_id:
                s = self.seat_dao.get_seat_by_id(it.seat_id)
                if s:
                    seat_names.append(s.seat_number)
            else:
                ga_quantity += (it.quantity or 1)

        # Add-ons
        addons = self.booking_addon_dao.get_addons_by_booking(booking.id)
        addon_lines = []
        for a in addons:
            ad_model = self.event_addon_dao.get_addon_by_id(a.addon_id)
            name = ad_model.name if ad_model else "Add-on"
            addon_lines.append(f"{name} (Qty: {a.quantity})")

        # ------------------------------------------------------------- #
        # Generate QR Code in memory
        # ------------------------------------------------------------- #
        qr_payload = ticket.qr_data or f"/verify/{ticket.ticket_token}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=2,
        )
        qr.add_data(qr_payload)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#490E13", back_color="white")
        
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        reportlab_qr = Image(qr_buffer, width=120, height=120)

        # ------------------------------------------------------------- #
        # PDF Document Construction
        # ------------------------------------------------------------- #
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Color Palette
        burgundy = colors.HexColor("#490E13")
        primary_orange = colors.HexColor("#F54828")
        dark_text = colors.HexColor("#1A1A1A")
        muted_text = colors.HexColor("#666666")
        surface_bg = colors.HexColor("#FAFAF8")
        border_color = colors.HexColor("#E5E5E0")

        # Custom Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=burgundy,
        )
        brand_style = ParagraphStyle(
            "BrandHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=primary_orange,
        )
        label_style = ParagraphStyle(
            "LabelStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=muted_text,
        )
        val_style = ParagraphStyle(
            "ValStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=dark_text,
        )
        val_bold_style = ParagraphStyle(
            "ValBoldStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=dark_text,
        )
        badge_style = ParagraphStyle(
            "BadgeStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#28A745"),
            alignment=2,  # Right align
        )
        small_style = ParagraphStyle(
            "SmallStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=muted_text,
            alignment=1,  # Center align
        )

        story = []

        # 1. Header Bar: Brand + Official Pass
        header_data = [
            [
                Paragraph("🎟️ <b>SeatMeUp</b>", brand_style),
                Paragraph(f"STATUS: <b>{ticket.ticket_status.upper()}</b>", badge_style),
            ]
        ]
        t_header = Table(header_data, colWidths=[300, 240])
        t_header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t_header)

        story.append(HRFlowable(width="100%", thickness=2, color=primary_orange, spaceBefore=4, spaceAfter=12))

        # 2. Event Title & Category
        event_title = event.title if event else "Event Admission Ticket"
        cat_name = category.name if category else "General Event"
        story.append(Paragraph(f"<b>{event_title}</b>", title_style))
        story.append(Paragraph(f"<font color='{muted_text}'>Category: {cat_name}</font>", val_style))
        story.append(Spacer(1, 14))

        # 3. Main Info Grid (Left: Event & Attendee Details, Right: QR Code)
        event_date_str = str(event.event_date) if event else ""
        start_time_str = str(event.start_time) if event else ""
        end_time_str = f" to {event.end_time}" if event and event.end_time else ""
        venue_name_str = venue.name if venue else "Main Venue"
        venue_addr_str = f"{venue.address}, {venue.city}" if venue and venue.address else ""
        cust_name_str = user.name if user else "Customer"
        cust_email_str = user.email if user else ""

        # Seats description
        if is_seated and seat_names:
            seats_desc = ", ".join(seat_names)
        elif not is_seated:
            seats_desc = f"{ga_quantity} × General Admission Ticket(s)"
        else:
            seats_desc = "Standard Admission"

        addons_desc = ", ".join(addon_lines) if addon_lines else "None"

        left_details_data = [
            [Paragraph("DATE & TIME", label_style), Paragraph(f"{event_date_str} • {start_time_str}{end_time_str}", val_bold_style)],
            [Paragraph("VENUE", label_style), Paragraph(f"<b>{venue_name_str}</b><br/>{venue_addr_str}", val_style)],
            [Paragraph("ATTENDEE", label_style), Paragraph(f"<b>{cust_name_str}</b> ({cust_email_str})", val_style)],
            [Paragraph("SEATS / ADMISSION", label_style), Paragraph(f"<b>{seats_desc}</b>", val_bold_style)],
            [Paragraph("ADD-ONS", label_style), Paragraph(addons_desc, val_style)],
            [Paragraph("BOOKING REF", label_style), Paragraph(f"<b>{booking.booking_reference}</b>", val_bold_style)],
            [Paragraph("TICKET TOKEN", label_style), Paragraph(f"<font name='Courier'>{ticket.ticket_token}</font>", val_style)],
        ]

        t_left = Table(left_details_data, colWidths=[120, 260])
        t_left.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))

        # Right side box containing QR and instructions
        qr_cell_data = [
            [reportlab_qr],
            [Paragraph("<b>SCAN AT ENTRANCE</b>", ParagraphStyle("QRLbl", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11, alignment=1, textColor=burgundy))],
            [Paragraph(f"<font size=7 color='{muted_text}'>Token: {ticket.ticket_token[:12]}...</font>", ParagraphStyle("QRSub", parent=styles["Normal"], alignment=1))],
        ]
        t_qr_box = Table(qr_cell_data, colWidths=[140])
        t_qr_box.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), surface_bg),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        # Combine Left Details + Right QR Box into one row
        main_grid = Table([[t_left, t_qr_box]], colWidths=[380, 160])
        main_grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(main_grid)

        story.append(Spacer(1, 14))
        story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceBefore=4, spaceAfter=10))

        # 4. Payment & Reward Breakdown Table
        tot_paid = float(booking.total_amount)
        disc_amt = float(booking.discount_amount or 0.0)
        cb_amt = float(booking.cashback_amount or 0.0)
        subtot = round(tot_paid + disc_amt, 2)

        pricing_data = [
            [Paragraph("Subtotal", val_style), Paragraph(f"${subtot:.2f}", val_style)],
            [Paragraph("Discount", val_style), Paragraph(f"-${disc_amt:.2f}", val_style)],
            [Paragraph("<b>Total Paid</b>", val_bold_style), Paragraph(f"<b>${tot_paid:.2f}</b>", val_bold_style)],
            [Paragraph("🎁 <b>2% Cashback Earned</b>", val_style), Paragraph(f"+${cb_amt:.2f}", badge_style)],
        ]
        t_pricing = Table(pricing_data, colWidths=[400, 140])
        t_pricing.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("LINEABOVE", (0, 2), (-1, 2), 0.5, border_color),
        ]))
        story.append(t_pricing)

        story.append(Spacer(1, 16))

        # 5. Footer Notice & Security
        issued_date_str = ticket.issued_at.strftime("%Y-%m-%d %H:%M UTC") if ticket.issued_at else ""
        story.append(Paragraph(
            f"Issued by SeatMeUp on {issued_date_str} • This digital ticket is subject to the SeatMeUp Terms & Conditions.<br/>"
            "Please present this PDF on your mobile device or print it clearly for door barcode scanning.",
            small_style,
        ))

        # Build document
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
