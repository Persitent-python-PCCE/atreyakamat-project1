class Venue:
    def __init__(self, id=None, name=None, address=None, capacity=0):
        self.id = id
        self.name = name
        self.address = address
        self.capacity = capacity

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "capacity": self.capacity,
        }
