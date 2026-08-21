# SeatMeUp — API Testing Guide (Postman)

This document explains how to test the basic SeatMeUp REST API with **Postman**.
Every endpoint returns the same shape:

**Success**
```json
{ "success": true, "message": "...", "data": { ... } }
```
**Error**
```json
{ "success": false, "message": "..." }
```

Common HTTP status codes used by these endpoints:
`200` OK · `201` Created · `400` Bad Request · `404` Not Found · `409` Conflict · `500` Server Error

---

## 0. Before you start

1. Make sure MySQL is running and your `.env` file has correct `DB_*` values.
2. Make sure all tables exist. The API does **not** create tables automatically.
   If they don't exist yet, run inside a Python shell once:
   ```python
   from app import create_app, init_db
   app = create_app()
   init_db(app)
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```
   Default base URL for all requests below: **`http://127.0.0.1:5000`**
4. In Postman, set the default header on every request:
   ```
   Content-Type: application/json
   Accept: application/json
   ```

---

## 1. Recommended testing order

These build on each other — later steps depend on rows created in earlier steps.
Run them top-to-bottom and note the new `id` returned in each `data` block.

| Step | Method | Endpoint                                 | Purpose                          |
|------|--------|------------------------------------------|----------------------------------|
| 1    | POST   | `/api/categories`                        | Create a category                |
| 2    | POST   | `/api/venues`                            | Create a venue                   |
| 3    | POST   | `/api/users`                             | Create a user (organiser/admin)  |
| 4    | POST   | `/api/events`                            | Create an event (uses 1, 2, 3)   |
| 5    | POST   | `/api/venues/<venue_id>/seats` *(n/a yet)* | *(Seats need a DAO create route for now just create them via the DB or add later. Reading is available — see Steps 6/7.)* Note: there is currently no POST /api/...seats endpoint; you may insert seats manually or skip Step 5 and just read seats with Step 7. |
| 6    | GET    | `/api/events/<event_id>`                 | Retrieve the event               |
| 7    | GET    | `/api/venues/<venue_id>/seats`            | Retrieve seats of a venue        |
| 8    | POST   | `/api/bookings`                          | Create a booking for the event   |
| 9    | GET    | `/api/bookings/<booking_id>`             | Retrieve the booking             |
| 10   | GET    | `/api/bookings/<booking_id>/ticket`       | Retrieve the ticket of a booking |
| 11   | POST   | `/api/tickets/<token>/verify`            | Verify a ticket (scan simulation)|

> Note on Step 5: the current basic API exposes **read** endpoints for seats
> (`GET /api/venues/<venue_id>/seats` and `GET /api/events/<event_id>/seats`)
> but no `POST /api/seats` to create them. You can create seats directly in
> the database for now, or skip Step 5 entirely — creating a booking does not
> require seats to exist in this basic stage.

---

## 2. Important endpoints

### 2.1 Create a category
- **POST** `/api/categories`
- Purpose: register a new event category (e.g. "Concert").
- Request body:
```json
{ "name": "Concert", "description": "Live music events" }
```
- Expected response (201):
```json
{
  "success": true,
  "message": "Category created",
  "data": {
    "id": 1,
    "name": "Concert",
    "description": "Live music events",
    "created_at": "2026-08-21T12:00:00"
  }
}
```
- Note the `data.id` (here `1`) — you'll use it for the event.

### 2.2 Create a venue
- **POST** `/api/venues`
- Purpose: register a physical place where events happen.
- Request body:
```json
{
  "name": "Grand Hall",
  "address": "1 Main Street",
  "city": "London",
  "state": "",
  "capacity": 1000,
  "venue_type": "seated"
}
```
- Expected response (201): success envelope with `data.id`. Note that id (e.g. `1`).

### 2.3 Create a user (event organiser)
- **POST** `/api/users`
- Purpose: create a user who can create events and book tickets.
- Request body:
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "password_hash": "hashed-value-placeholder",
  "role": "admin"
}
```
- Expected response (201): success envelope with the new user's id (e.g. `1`).
- Note: the API accepts `password_hash` directly at this basic stage. Real
  hashing will be added later in the Service layer.

### 2.4 Create an event
- **POST** `/api/events`
- Purpose: schedule a new event tied to a category and venue, created by a user.
- Request body (use real ids returned by Steps 1, 2, 3):
```json
{
  "title": "Rock Night",
  "category_id": 1,
  "venue_id": 1,
  "created_by": 1,
  "event_date": "2026-12-31",
  "start_time": "20:00:00",
  "end_time": "23:00:00",
  "description": "A great rock concert",
  "base_price": 50.00,
  "status": "published",
  "requires_seats": true
}
```
- Expected response (201): success envelope with `data.id` (e.g. `1`).
- If the foreign keys don't exist you'll get a `500` because MySQL rejects
  the FK. Make sure Steps 1–3 succeeded.

### 2.5 Retrieve an event by id
- **GET** `/api/events/1`
- Purpose: fetch a single event.
- Expected response (200): success envelope with the event fields.

### 2.6 List upcoming events
- **GET** `/api/events/upcoming`
- Purpose: every event whose `event_date` is in the future, soonest first.
- Expected response (200): success envelope with a list.

### 2.7 Search events by title
- **GET** `/api/events/search?q=rock`
- Purpose: events whose title contains "rock" (case-insensitive).

### 2.8 List seats of a venue
- **GET** `/api/venues/1/seats`
- Purpose: every seat in the venue (active and inactive).

### 2.9 List available seats for an event
- **GET** `/api/events/1/seats`
- Purpose: the venue's *active* seats for this event. The real
  hold/sold filtering is a Service-layer concern — see the route file note.

### 2.10 Create a booking
- **POST** `/api/bookings`
- Purpose: create a new booking for an event by a user.
- Request body:
```json
{
  "user_id": 1,
  "event_id": 1,
  "total_amount": 100.00,
  "status": "pending"
}
```
- Expected response (201): success envelope with the new booking,
  including an auto-generated `booking_reference` like `SMU-7d3c9a2b1f04`.
- Make a note of `data.id` and `data.booking_reference`.

### 2.11 Retrieve a booking by id
- **GET** `/api/bookings/1`
- Expected response (200): success envelope with the booking fields.

### 2.12 Retrieve a booking by reference
- **GET** `/api/bookings/reference/SMU-7d3c9a2b1f04`
- Use the `booking_reference` returned by Step 10.

### 2.13 List a user's bookings
- **GET** `/api/users/1/bookings`
- Expected response (200): success envelope with a list (possibly empty).

### 2.14 Retrieve the ticket of a booking
- **GET** `/api/bookings/1/ticket`
- Purpose: get the (single) ticket linked to a booking.
- Expected response: `404` if no ticket exists yet for that booking, else `200`.
- In this basic stage there is **no public route** to create a ticket
  automatically. The Service layer later will create the ticket atomically
  when the booking is confirmed. For now you can insert a ticket via the DB
  to test the verify endpoint, or skip Step 11.

### 2.15 Verify a ticket (scan simulation)
- **POST** `/api/tickets/<token>/verify`
- Purpose: record a verification attempt. The `<token>` is the ticket's
  `ticket_token`.
- Request body:
```json
{ "verification_status": "valid" }
```
- Expected response (201): success envelope with the new verification row.
- Note: in this basic stage, the API simply **records** whatever status the
  client sends and does not flip the ticket's own status; that logic lives
  in the future Service layer.

---

## 3. Other CRUD endpoints (summary)

These work the same way (POST = create, GET = list + read by id,
PUT = update, DELETE = delete). All bodies use the same field names found
in the existing SQLAlchemy models.

| Resource            | Endpoints |
|---------------------|-----------|
| Users               | `POST /api/users`, `GET /api/users`, `GET /api/users/<id>`, `GET /api/users/email/<email>`, `PUT /api/users/<id>`, `DELETE /api/users/<id>` |
| Categories          | `POST /api/categories`, `GET /api/categories`, `GET /api/categories/<id>`, `PUT /api/categories/<id>`, `DELETE /api/categories/<id>` |
| Venues              | `POST /api/venues`, `GET /api/venues`, `GET /api/venues/<id>`, `PUT /api/venues/<id>`, `DELETE /api/venues/<id>` |
| Events              | `POST /api/events`, `GET /api/events`, `GET /api/events/<id>`, `PUT /api/events/<id>`, `DELETE /api/events/<id>`, `GET /api/events/upcoming`, `GET /api/events/category/<category_id>`, `GET /api/events/search?q=…` |
| Seats               | `GET /api/venues/<venue_id>/seats`, `GET /api/events/<event_id>/seats` |
| Bookings            | `POST /api/bookings`, `GET /api/bookings/<id>`, `GET /api/bookings/reference/<reference>`, `GET /api/users/<user_id>/bookings`, `PUT /api/bookings/<id>`, `DELETE /api/bookings/<id>` |
| Tickets             | `GET /api/tickets/<token>`, `GET /api/bookings/<booking_id>/ticket`, `POST /api/tickets/<token>/verify` |
| Notifications       | `GET /api/users/<user_id>/notifications`, `POST /api/notifications`, `PUT /api/notifications/<id>/read` |
| Promo codes         | `POST /api/promos`, `GET /api/promos`, `GET /api/promos/<id>`, `PUT /api/promos/<id>`, `DELETE /api/promos/<id>` |

---

## 4. Tips for Postman beginners

- Create one **environment** (`SeatMeUp Local`) with a variable `base_url`
  set to `http://127.0.0.1:5000`. Use `{{base_url}}` in every request URL.
- After each POST that creates a row, copy the returned `id` somewhere —
  you'll reuse it as a path parameter in later steps.
- Use **Collections** to group requests by resource (Users, Events, …).
- The **Tests** tab can read `pm.response.json().data.id` and set it as an
  environment variable automatically, e.g.
  ```js
  pm.environment.set("event_id", pm.response.json().data.id);
  ```
  Then the next request can use `{{event_id}}` instead of typing the number.
- If a `500` comes back unexpectedly, check the Flask console output for
  the real exception (the API does not expose the raw stack trace to the
  client on purpose, but you'll see it in the server log).

---

## 5. What is NOT supported yet (by design)

These are intentionally NOT included in this basic API layer:

- Real authentication / JWT / sessions
- Password hashing at the API boundary
- Email/PDF/QR image generation
- Cashback calculation, automatic ticket expiration
- The 1-minute seat-hold workflow
- Admin password confirmation for rescheduling
- The booking transaction (multiple DAO writes tied together)
- File upload handling
- Frontend pages

All of those belong to the future Service layer and are intentionally
deferred. The route signatures here have been designed so the Service can
slot in between routes and DAOs without changing the URLs.
