# Services/user_service.py
#
# UserService — the business-logic layer for the `users` table.
#
# Flow it sits in:
#
#     api/user_routes.py  (Controller — receives JSON, calls Service)
#              |
#              v
#       UserService  (THIS FILE — validates, decides, calls DAO)
#              |
#              v
#        UserDAO   (DAO — only does SQLAlchemy calls)
#              |
#              v
#         User model  -> MySQL
#
# Responsibilities of THIS file:
#   - check that required fields exist and look reasonable
#   - check business rules (e.g. "email must be unique")
#   - decide what fields a User gets when created
#   - coordinate fetch-then-update / fetch-then-delete
#   - catch DAO exceptions and turn them into a friendly failure result
#
# What this file does NOT do:
#   - import Flask, request, jsonify (that is the Controller's job)
#   - run SQL directly (that is the DAO's job)
#   - hash passwords (deferred to a later authentication phase — at this
#     stage `password_hash` is just treated as a plain model field that the
#     caller supplies)
#
# How every method returns:
#   Every method returns a plain dict, built with ok()/fail() from
#   Services/_result.py. The Controller turns it into an HTTP response.
#
# Why we catch broad `Exception`:
#   The DAO rolls back the transaction before re-raising. We do not care
#   WHAT specific error happened (IntegrityError, OperationalError, ...).
#   We just convert any failure into a `success: False` result with a
#   simple message and a 500 status. The user message never leaks the
#   raw SQLAlchemy stack trace (a security + UX choice).

from DAO import UserDAO
from models.user import User
from api.serializers import user_to_dict
from Services._result import ok, fail


class UserService:
    """Business operations for users.

    The DAO is instantiated once and reused. DAO objects hold no state,
    so this is safe and keeps method bodies short.
    """

    def __init__(self):
        self.user_dao = UserDAO()

    # ---------------------------------------------------------------- #
    # CREATE
    # ---------------------------------------------------------------- #
    def create_user(self, data: dict) -> dict:
        """Create one user.

        Required fields in `data`: name, email, password_hash
        Optional fields:  role (default "customer"), phone, id_document

        Returns a result dict (see Services/_result.py):
          - success 201 + user dict    -> created
          - fail    400                 -> missing required field
          - fail    409                 -> email already registered
          - fail    500                 -> database error
        """
        # 1) Basic required-field validation (kept simple on purpose).
        required = ("name", "email", "password_hash")
        for field in required:
            value = data.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return fail(f"Missing required field: {field}", 400)

        # 2) Business rule: email must be unique.
        # We check BEFORE the insert so we can return a clean 409 to the
        # caller. (MySQL would also reject it via the unique constraint,
        # but catching it early gives a friendlier message and avoids a
        # needless rollback in the DAO.)
        if self.user_dao.get_user_by_email(data["email"]) is not None:
            return fail("Email already registered", 409)

        # 3) Build the model object. Defaults come from the model, but we
        # also set them here for clarity so a beginner can read the
        # assignment list and know what is being inserted.
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=data["password_hash"],    # already hashed by caller (later)
            role=data.get("role", "customer"),
            phone=data.get("phone"),
            id_document=data.get("id_document"),
        )

        # 4) Persist via the DAO. If anything goes wrong, the DAO has
        # already rolled back; we just turn the exception into a 500.
        try:
            saved = self.user_dao.create_user(user)
        except Exception:
            return fail("Could not create user", 500)

        return ok("User created", user_to_dict(saved), status=201)

    # ---------------------------------------------------------------- #
    # READ
    # ---------------------------------------------------------------- #
    def get_user_by_id(self, user_id: int) -> dict:
        """Get a user by primary key. 404 if not found."""
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)
        return ok("User retrieved", user_to_dict(user))

    def get_user_by_email(self, email: str) -> dict:
        """Get a user by email. 404 if not found. Empty string is 400."""
        if not email:
            return fail("Email is required", 400)
        user = self.user_dao.get_user_by_email(email)
        if user is None:
            return fail("User not found", 404)
        return ok("User retrieved", user_to_dict(user))

    def get_all_users(self) -> dict:
        """List every user."""
        users = self.user_dao.get_all_users()
        return ok("Users retrieved", [user_to_dict(u) for u in users])

    # ---------------------------------------------------------------- #
    # UPDATE
    # ---------------------------------------------------------------- #
    def update_user(self, user_id: int, data: dict) -> dict:
        """Update an existing user's editable fields.

        Only fields the client actually sent are changed. If the email is
        changed, we re-check uniqueness (it must not belong to another user).
        """
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)

        # name
        if "name" in data:
            name = data["name"]
            if name is None or (isinstance(name, str) and name.strip() == ""):
                return fail("name cannot be empty", 400)
            user.name = name

        # email (with uniqueness check)
        if "email" in data:
            email = data["email"]
            if email is None or (isinstance(email, str) and email.strip() == ""):
                return fail("email cannot be empty", 400)
            existing = self.user_dao.get_user_by_email(email)
            if existing is not None and existing.id != user.id:
                return fail("Email already in use", 409)
            user.email = email

        # password_hash
        if "password_hash" in data:
            user.password_hash = data["password_hash"]

        # role
        if "role" in data:
            user.role = data["role"]

        # phone
        if "phone" in data:
            user.phone = data["phone"]

        # id_document
        if "id_document" in data:
            user.id_document = data["id_document"]

        # is_active
        if "is_active" in data:
            user.is_active = bool(data["is_active"])

        try:
            self.user_dao.update_user(user)
        except Exception:
            return fail("Could not update user", 500)

        return ok("User updated", user_to_dict(user))

    # ---------------------------------------------------------------- #
    # DELETE
    # ---------------------------------------------------------------- #
    def delete_user(self, user_id: int) -> dict:
        """Delete a user by id. 404 if not found."""
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)

        try:
            self.user_dao.delete_user(user)
        except Exception:
            return fail("Could not delete user", 500)

        return ok("User deleted")
