# SeatMeUp — System Architecture

This document describes the layered architecture of the SeatMeUp backend application. It is written to be simple, explicit, and beginner-friendly.

---

## 1. Architectural Overview

SeatMeUp follows a strict **5-layer architecture**:

```
        HTTP Client (Postman / Browser / Mobile App)
                             │
                             ▼
                    ┌─────────────────┐
                    │   Controller    │  (HTTP / API layer)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Service     │  (Business logic layer)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │       DAO       │  (Data Access Object layer)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ SQLAlchemy Model│  (Database table schema)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      MySQL      │  (Relational database)
                    └─────────────────┘
```

---

## 2. Responsibilities of Each Layer

### Layer 1: Controller (`Controller/`)
- **What it is**: The entry point for HTTP requests.
- **Responsibilities**:
  - Receive the incoming HTTP request (`GET`, `POST`, `PUT`, `DELETE`).
  - Read JSON payloads (`request.get_json()`) or query arguments (`request.args`).
  - Perform basic request sanity checks.
  - Call the corresponding method on the **Service** layer.
  - Convert the Service dictionary result into JSON using Flask's `jsonify()`.
  - Return the appropriate HTTP status code (`200`, `201`, `400`, `404`, `409`, `500`).
- **What it NEVER does**:
  - Never query the database directly.
  - Never import or use DAOs directly.
  - Never write SQL or SQLAlchemy queries.
  - Never calculate business values (discounts, balances, totals).

---

### Layer 2: Service (`Services/`)
- **What it is**: The business logic and validation coordinator.
- **Responsibilities**:
  - Accept plain Python arguments (integers, strings, dicts).
  - Validate required business inputs and rules (e.g., uniqueness of email, foreign key entity existence).
  - Coordinate multiple DAOs when an operation spans several tables.
  - Handle exceptions from DAOs and roll back transactions safely.
  - Return consistent result dictionaries using `ok(...)` and `fail(...)`:
    ```python
    # Success
    {"success": True, "message": "User created", "data": {...}, "status": 201}

    # Failure
    {"success": False, "message": "Email already registered", "status": 409}
    ```
- **What it NEVER does**:
  - Never import Flask `request` or `Response` objects.
  - Never call `jsonify()`.
  - Never render HTML templates.
  - Never run raw SQL queries directly.

---

### Layer 3: Data Access Object (DAO) (`DAO/`)
- **What it is**: The database query layer.
- **Responsibilities**:
  - Isolate all database queries in one place for each model (e.g., `UserDAO`, `EventDAO`).
  - Add, commit, query, update, and delete SQLAlchemy model objects.
  - Guarantee transaction safety with `try ... db.session.commit() except: db.session.rollback(); raise`.
- **What it NEVER does**:
  - Never make business decisions (e.g., who is authorized or what error message to show users).
  - Never format HTTP responses.

---

### Layer 4: SQLAlchemy Model (`models/`)
- **What it is**: Python class representations of database tables.
- **Responsibilities**:
  - Define columns, data types, constraints (e.g. `primary_key`, `unique`, `nullable`, `default`).
  - Define relationships (`back_populates`, foreign keys).

---

### Layer 5: MySQL Database
- **What it is**: The persistent relational database where records are stored in physical tables.

---

## 3. Step-by-Step Example: Creating a User

Here is the complete journey of a `POST /api/users` request:

```
1. Client sends POST /api/users with JSON:
   {
       "name": "Alice Smith",
       "email": "alice@example.com",
       "password_hash": "secret123",
       "role": "customer"
   }
              │
              ▼
2. UserController (Controller/user_controller.py)
   - Reads request JSON.
   - Calls UserService.create_user(data).
              │
              ▼
3. UserService (Services/user_service.py)
   - Checks required fields: name, email, password_hash.
   - Calls UserDAO.get_user_by_email("alice@example.com") to check uniqueness.
   - Instantiates User model object.
   - Calls UserDAO.create_user(user).
              │
              ▼
4. UserDAO (DAO/user_dao.py)
   - Runs db.session.add(user) and db.session.commit().
   - Database assigns an autoincrement ID.
   - Returns the persisted User model object.
              │
              ▼
5. User Model (models/user.py)
   - Represents the row in the `users` table.
              │
              ▼
6. MySQL Database
   - Stores the row permanently.
              │
              ▼
7. Response unwinds back up:
   - UserDAO returns User instance to UserService.
   - UserService converts User to dict using serializer and returns ok("User created", data, 201).
   - UserController converts dict to jsonify() with HTTP 201.
   - Client receives:
     {
         "success": true,
         "message": "User created",
         "data": {
             "id": 1,
             "name": "Alice Smith",
             "email": "alice@example.com",
             "role": "customer",
             ...
         }
     }
```

---

## 4. Summary of Modules

| Resource | Controller | Service | DAO | Model |
| :--- | :--- | :--- | :--- | :--- |
| **Users** | `user_controller.py` | `user_service.py` | `user_dao.py` | `user.py` |
| **Categories** | `category_controller.py` | `category_service.py` | `category_dao.py` | `category.py` |
| **Venues** | `venue_controller.py` | `venue_service.py` | `venue_dao.py` | `venue.py` |
| **Events** | `event_controller.py` | `event_service.py` | `event_dao.py` | `event.py` |
| **Seats** | `seat_controller.py` | `seat_service.py` | `seat_dao.py` | `seat.py` |
| **Event Add-ons** | — | `event_addon_service.py` | `event_addon_dao.py` | `event_addon.py` |
| **Seat Holds** | — | `seat_hold_service.py` | `seat_hold_dao.py` | `seat_hold.py` |
| **Bookings** | `booking_controller.py` | `booking_service.py` | `booking_dao.py` | `booking.py` |
| **Tickets** | `ticket_controller.py` | `ticket_service.py` | `ticket_dao.py` | `ticket.py` |
| **Promos** | `promo_controller.py` | `promo_service.py` | `promo_dao.py` | `promo_code.py` |
| **Rewards** | — | `reward_service.py` | `reward_transaction_dao.py` | `reward_transaction.py` |
| **Notifications**| `notification_controller.py`| `notification_service.py`| `notification_dao.py`| `notification.py` |
| **Reschedules** | — | `event_reschedule_service.py` | `event_reschedule_dao.py` | `event_reschedule.py` |
| **Files** | — | `uploaded_file_service.py` | `uploaded_file_dao.py` | `uploaded_file.py` |
| **Email Logs** | — | `email_log_service.py` | `email_log_dao.py` | `email_log.py` |
