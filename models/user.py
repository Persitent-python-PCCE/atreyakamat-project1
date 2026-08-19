class User:
    def __init__(self, id=None, name=None, email=None, password_hash=None, role="customer"):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }
