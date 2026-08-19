class Booking:
    def __init__(self, id=None, user_id=None, event_id=None, booking_reference=None, status="pending"):
        self.id = id
        self.user_id = user_id
        self.event_id = event_id
        self.booking_reference = booking_reference
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "booking_reference": self.booking_reference,
            "status": self.status,
        }
