class Event:
    def __init__(self, id=None, title=None, description=None, venue_id=None, event_date=None):
        self.id = id
        self.title = title
        self.description = description
        self.venue_id = venue_id
        self.event_date = event_date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "venue_id": self.venue_id,
            "event_date": self.event_date,
        }
