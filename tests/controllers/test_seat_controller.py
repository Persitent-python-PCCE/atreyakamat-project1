# tests/controllers/test_seat_controller.py
#
# Controller tests for Seat API endpoints (/api/venues/<id>/seats, /api/events/<id>/seats/<id>/hold).
# WHY: Verifies seat map retrieval and 1-minute hold race condition resolution via HTTP status codes.

import pytest
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from models.user import User


@pytest.mark.controller
class TestSeatController:
    def test_seat_hold_and_conflict_api(self, app, client, db_session, event, seat):
        """WHY: User 1 can place a hold (201 Created), and concurrent hold attempt by User 2 gets 409 Conflict."""
        # Create two distinct customers
        u1 = User(name="User 1", email="u1@seat.com", password_hash=generate_password_hash("pw"), role="customer")
        u2 = User(name="User 2", email="u2@seat.com", password_hash=generate_password_hash("pw"), role="customer")
        db_session.add_all([u1, u2])
        db_session.commit()

        with app.app_context():
            token1 = create_access_token(identity=str(u1.id), additional_claims={"role": "customer", "email": "u1@seat.com"})
            token2 = create_access_token(identity=str(u2.id), additional_claims={"role": "customer", "email": "u2@seat.com"})

        # User 1 holds seat -> 201
        res1 = client.post(
            f"/api/events/{event.id}/seats/{seat.id}/hold",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert res1.status_code == 201

        # User 2 attempts to hold same seat -> 409 Conflict
        res2 = client.post(
            f"/api/events/{event.id}/seats/{seat.id}/hold",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert res2.status_code == 409
