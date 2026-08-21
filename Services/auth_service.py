# Services/auth_service.py
#
# AuthService — handles user registration, password hashing, credential verification,
# and JWT generation.
#
# Flow:
#     AuthController / Routes -> AuthService -> UserDAO -> User Model -> MySQL

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from DAO import UserDAO
from models.user import User
from api.serializers import user_to_dict
from Services._result import ok, fail


class AuthService:
    def __init__(self):
        self.user_dao = UserDAO()

    # ---------------------------------------------------------------- #
    # REGISTER
    # ---------------------------------------------------------------- #
    def register(self, data: dict) -> dict:
        """Register a new user with a hashed password.

        Required in `data`: name, email, password
        Optional: phone
        Default role is 'customer'.
        """
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        # 1. Validation
        if not name or (isinstance(name, str) and not name.strip()):
            return fail("Missing required field: name", 400)
        if not email or (isinstance(email, str) and not email.strip()):
            return fail("Missing required field: email", 400)
        if not password or (isinstance(password, str) and not password.strip()):
            return fail("Missing required field: password", 400)

        # 2. Check if email already exists
        existing_user = self.user_dao.get_user_by_email(email.strip())
        if existing_user is not None:
            return fail("Email already registered", 409)

        # 3. Hash the password using Werkzeug
        hashed_password = generate_password_hash(password)

        # 4. Create the User model object
        new_user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=hashed_password,
            role=data.get("role", "customer"),
            phone=data.get("phone"),
            is_active=True,
        )

        # 5. Persist through UserDAO
        try:
            saved_user = self.user_dao.create_user(new_user)
        except Exception:
            return fail("Could not register user", 500)

        return ok("User registered successfully", user_to_dict(saved_user), status=201)

    # ---------------------------------------------------------------- #
    # LOGIN
    # ---------------------------------------------------------------- #
    def login(self, email: str, password: str) -> dict:
        """Verify credentials and issue a JWT access token."""
        if not email or not password:
            return fail("Email and password are required", 400)

        user = self.user_dao.get_user_by_email(email.strip().lower())
        if user is None:
            return fail("Invalid email or password", 401)

        # Verify password hash
        if not check_password_hash(user.password_hash, password):
            return fail("Invalid email or password", 401)

        # Verify active status
        if not user.is_active:
            return fail("Account is inactive. Please contact support.", 403)

        # Generate JWT access token with user ID identity and role claims
        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role,
                "name": user.name,
                "email": user.email,
            },
        )

        response_data = {
            "token": token,
            "user": user_to_dict(user),
        }
        return ok("Login successful", response_data, status=200)

    # ---------------------------------------------------------------- #
    # GET CURRENT USER (ME)
    # ---------------------------------------------------------------- #
    def get_me(self, user_id: int) -> dict:
        """Get profile data for the authenticated user by ID."""
        user = self.user_dao.get_user_by_id(user_id)
        if user is None:
            return fail("User not found", 404)
        return ok("User profile retrieved", user_to_dict(user), status=200)
