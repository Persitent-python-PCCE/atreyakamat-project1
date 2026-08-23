# tests/conftest.py
#
# Global Pytest fixtures for SeatMeUp test suite.
# Provides clean, isolated in-memory database setups, Flask test client,
# JWT authentication tokens, and common test entity factories.

import os
import pytest
from datetime import date, timedelta, time
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app import create_app, db
from Config.config import TestingConfig
from models.user import User
from models.category import Category
from models.venue import Venue
from models.event import Event
from models.seat import Seat


def pytest_collection_modifyitems(config, items):
    """Automatically skip tests marked with @pytest.mark.mysql unless SEATMEUP_RUN_MYSQL_TESTS=1."""
    if os.getenv("SEATMEUP_RUN_MYSQL_TESTS") != "1":
        skip_mysql = pytest.mark.skip(reason="Live MySQL tests run only when SEATMEUP_RUN_MYSQL_TESTS=1")
        for item in items:
            if "mysql" in item.keywords:
                item.add_marker(skip_mysql)


@pytest.fixture(scope="session")
def app():
    """Create a single Flask application configured for testing with SQLite in-memory."""
    flask_app = create_app(TestingConfig)
    return flask_app


@pytest.fixture(autouse=True)
def app_ctx(app):
    """Ensure every test runs inside a valid Flask application context."""
    with app.app_context():
        yield


@pytest.fixture
def db_session(app):
    """Set up a fresh, isolated database for each test and tear it down cleanly."""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()
        # Dispose engine pool to close SQLite connections cleanly and eliminate ResourceWarnings
        if db.engine:
            db.engine.dispose()


@pytest.fixture
def client(app, db_session):
    """Provide a Flask test client for API and Controller tests."""
    return app.test_client()


@pytest.fixture
def admin_user(db_session):
    """Seed and return a standard active Admin user."""
    admin = User(
        name="Admin Tester",
        email="admin_fixture@seatmeup.com",
        password_hash=generate_password_hash("AdminPass123!"),
        role="admin",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def customer_user(db_session):
    """Seed and return a standard active Customer user."""
    customer = User(
        name="Customer Tester",
        email="customer_fixture@seatmeup.com",
        password_hash=generate_password_hash("CustPass123!"),
        role="customer",
        is_active=True,
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def admin_token(app, admin_user):
    """Generate a valid JWT access token for the admin user."""
    with app.app_context():
        return create_access_token(
            identity=str(admin_user.id),
            additional_claims={
                "role": admin_user.role,
                "name": admin_user.name,
                "email": admin_user.email,
            },
        )


@pytest.fixture
def customer_token(app, customer_user):
    """Generate a valid JWT access token for the customer user."""
    with app.app_context():
        return create_access_token(
            identity=str(customer_user.id),
            additional_claims={
                "role": customer_user.role,
                "name": customer_user.name,
                "email": customer_user.email,
            },
        )


@pytest.fixture
def auth_headers_admin(admin_token):
    """Authorization header dictionary for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_customer(customer_token):
    """Authorization header dictionary for customer requests."""
    return {"Authorization": f"Bearer {customer_token}"}


@pytest.fixture
def category(db_session):
    """Seed and return a default Category."""
    cat = Category(name="Concerts", description="Live music events")
    db_session.add(cat)
    db_session.commit()
    return cat


@pytest.fixture
def venue(db_session):
    """Seed and return a default seated Venue."""
    ven = Venue(
        name="Grand Symphony Hall",
        address="100 Music Lane",
        city="New York",
        state="NY",
        capacity=500,
        venue_type="seated",
    )
    db_session.add(ven)
    db_session.commit()
    return ven


@pytest.fixture
def event(db_session, category, venue, admin_user):
    """Seed and return a default published seated Event."""
    ev = Event(
        category_id=category.id,
        venue_id=venue.id,
        created_by=admin_user.id,
        title="Beethoven Symphony No. 9",
        description="Epic classical performance",
        event_date=date.today() + timedelta(days=14),
        start_time=time(19, 30, 0),
        booking_open=True,
        requires_seats=True,
        base_price=75.00,
        status="published",
    )
    db_session.add(ev)
    db_session.commit()
    return ev


@pytest.fixture
def seat(db_session, venue):
    """Seed and return a default active Seat in the venue."""
    s = Seat(
        venue_id=venue.id,
        seat_number="A-10",
        section_name="Orchestra",
        price=75.00,
        is_active=True,
    )
    db_session.add(s)
    db_session.commit()
    return s
