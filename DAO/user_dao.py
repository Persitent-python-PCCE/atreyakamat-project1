# DAO/user_dao.py
#
# UserDAO — the Data Access Object for the `users` table.
#
# What this file does:
#   - It contains ONE class: UserDAO.
#   - Every method in this class performs ONE database operation on the User model.
#   - It does NOT hash passwords, check roles, validate emails, send emails,
#     or make any business decision. Those jobs belong to the Service layer.
#
# How it talks to the database:
#   - `db` is the Flask-SQLAlchemy object from app.py (it manages the connection).
#   - `db.session` is the workspace where SQLAlchemy tracks pending changes.
#     We tell it what to do, then call commit() to actually run the SQL.
#   - `User` is the SQLAlchemy model class from models/user.py. It represents
#     one row in the `users` table.
#
# Transaction safety pattern used in every "write" method:
#       try:
#           ... do the change ...
#           db.session.commit()        # actually save to the database
#       except Exception:
#           db.session.rollback()      # undo pending changes if anything failed
#           raise                      # re-raise so the caller (Service) sees the error
#
# We re-raise the exception so the Service above can decide what to do
# (return a friendly error message, log it, etc.). The DAO does NOT decide
# how to present errors to the user — that is also a Service/Controller job.

from app import db
from models.user import User


class UserDAO:
    """Database operations for the User model.

    Every method here is a thin wrapper around SQLAlchemy.
    No business logic, no authentication, no password hashing.
    """

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def create_user(self, user: User) -> User:
        """Insert a brand-new User row into the database.

        Steps:
          1. Add the object to the SQLAlchemy session (this stages the INSERT,
             it does NOT run any SQL yet).
          2. Commit the session — this is where the real INSERT happens.
          3. If commit works, return the same user object. SQLAlchemy will
             have filled in `user.id` automatically (the new primary key).

        If anything goes wrong (e.g. duplicate email because email is unique),
        we rollback so the session is clean for the next request, then
        re-raise the exception so the caller can handle it.

        Args:
            user: A User() object built by the Service. Its fields like
                  name, email, password_hash, role should already be set.
                  The DAO does not check or modify them.

        Returns:
            The same User object, now with an `id` attached.
        """
        try:
            db.session.add(user)       # stage the INSERT
            db.session.commit()        # actually run: INSERT INTO users ...
            return user
        except Exception:
            db.session.rollback()      # clean up the broken session
            raise                      # let the Service see the failure

    # ------------------------------------------------------------------ #
    # READ (by primary key)
    # ------------------------------------------------------------------ #
    def get_user_by_id(self, user_id: int) -> User | None:
        """Fetch a single user using their primary key (id).

        Uses db.session.get(User, user_id) which is the simplest way to
        load one row by primary key in SQLAlchemy 2.x.

        Args:
            user_id: The integer id of the user.

        Returns:
            A User object if found, or None if no user has that id.
            This method never raises on "not found" — None is a normal result.
        """
        # No try/except needed: a GET by primary key does not need rollback.
        # If the database connection itself is broken, the exception will
        # bubble up naturally to the Service.
        return db.session.get(User, user_id)

    # ------------------------------------------------------------------ #
    # READ (by email — used for login)
    # ------------------------------------------------------------------ #
    def get_user_by_email(self, email: str) -> User | None:
        """Fetch a single user by their email address.

        This is the lookup used during login: the Service asks "does a user
        with this email exist?" and gets back either the User object or None.

        Args:
            email: The email string to search for.

        Returns:
            A User object if found, or None if no user has that email.
        """
        # User.query is shortcut to db.session.query(User).
        # .filter_by(email=email) adds WHERE email = ?  (only equality).
        # .first() returns the first matching row, or None if no rows match.
        return User.query.filter_by(email=email).first()

    # ------------------------------------------------------------------ #
    # READ (all rows)
    # ------------------------------------------------------------------ #
    def get_all_users(self) -> list[User]:
        """Return every user in the database as a list of User objects.

        Be careful: on a large table this loads every row into memory.
        For SeatMeUp at beginner scale this is fine; pagination can be
        added later if needed (that would be a new method, not a change here).

        Returns:
            A Python list of User objects. Empty list if the table is empty.
        """
        # User.query.all()  ->  SELECT * FROM users;
        return User.query.all()

    # ------------------------------------------------------------------ #
    # UPDATE
    # ------------------------------------------------------------------ #
    def update_user(self, user: User) -> User:
        """Save changes that were already made to a User object.

        Important detail for beginners:
          - SQLAlchemy tracks changes automatically. When the Service does
            something like  user.name = "Alice"  on an object that was loaded
            from the database, SQLAlchemy notices and stages an UPDATE.
          - This method does NOT modify any field. It only commits whatever
            changes the Service has already applied to `user`.
          - That keeps the DAO dumb: it has no idea WHICH fields changed.

        Args:
            user: A User object that was fetched earlier (e.g. via
                  get_user_by_id) and then modified by the Service.

        Returns:
            The same User object, with changes now persisted to the DB.
        """
        try:
            db.session.commit()        # runs: UPDATE users SET ... WHERE id = ?
            return user
        except Exception:
            db.session.rollback()      # undo the attempted UPDATE
            raise

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def delete_user(self, user: User) -> bool:
        """Delete one user row from the database.

        The caller must pass an actual User object that exists in the DB
        (typically one returned by get_user_by_id or get_user_by_email).
        The DAO does not look up the user by itself — the Service decides
        which user to delete.

        Args:
            user: A User object to delete.

        Returns:
            True if the delete + commit succeeded.

        Raises:
            Exception if the commit fails; in that case the session is
            rolled back so it stays usable.
        """
        try:
            db.session.delete(user)    # stage the DELETE
            db.session.commit()        # actually run: DELETE FROM users WHERE id = ?
            return True
        except Exception:
            db.session.rollback()
            raise
