# SeatMeUp — Database Model Blueprint

> Status: **DRAFT — for review only.** No models are implemented as part of this document.
> The next step after approval is implementing **only** the `User` model, then reviewing each model one-by-one.

## Purpose

This document is the blueprint for every SQLAlchemy model SeatMeUp will eventually need.
It defines what each model represents, its fields, its relationships, and the business
rules attached to it, so each model can be implemented and reviewed one at a time.

Nothing in this document changes the current architecture. It only describes the target
data model.

---

## Current foundation (what already exists)

| Item | Status |
| --- | --- |
| Flask app factory | `app.py` — `create_app()` |
| SQLAlchemy instance | `db = SQLAlchemy()` in `app.py` |
| Database | MySQL (`mysql+pymysql://...`), database name `seatmeup` |
| Base model | `models/base_model.py` — abstract `BaseModel(db.Model)` with `id` (Integer, primary key) |
| **`User` model** | **Already implemented** in `models/user.py` as a real SQLAlchemy model |
| `Event`, `Venue`, `Booking` | Currently **plain Python placeholder classes** (not SQLAlchemy models yet) |
| Model registry | `models/__init__.py` imports `BaseModel` + `User`; the 19 planned models are listed in a comment |

### Conventions used in this document

- Every model extends `BaseModel` and therefore inherits `id = db.Column(db.Integer, primary_key=True)`.
- Every model uses a lowercase plural table name (e.g. `users`).
- Timestamps follow the existing `User` pattern:
  `created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)` and
  `updated_at` with `onupdate=datetime.utcnow`.
- Field notation: `Type (constraints) → FK target`
  - `PK` = primary key, `NN` = NOT NULL / required, `UQ` = unique, `DF` = default.
- Items marked **"To be decided"** are not yet fixed in the SeatMeUp scope. They are
  deliberately left open instead of being invented.
- Items marked **"Proposal"** are a recommended design. They must be confirmed during
  the per-model review before implementation.

---

# Part A — The 19 models

## 1. User — ✅ already implemented

**What it represents:** a person who uses SeatMeUp — a customer buying tickets, or an
admin managing events. This model already exists in `models/user.py` and is shown here
as the reference for all other models.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | from `BaseModel` |
| `name` | String(100) | | NN | | | — | |
| `email` | String(255) | | NN | ✅ | | — | login identifier |
| `password_hash` | String(255) | | NN | | | — | hash only, never plain text |
| `role` | String(20) | | NN | | `"customer"` | — | see enum below |
| `phone` | String(30) | | nullable | | | — | |
| `id_document` | String(255) | | nullable | | | — | uploaded ID reference |
| `reward_balance` | Integer | | NN | | `0` | — | cashback points balance |
| `is_active` | Boolean | | NN | | `True` | — | soft-disable accounts |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Enums / status values (`role`):** `customer` (default), `admin`. Additional roles
(e.g. venue manager) — **To be decided**.

**Relationships:**
- `bookings` — one User has many Bookings.
- `seat_holds` — one User has many SeatHolds.
- `tickets` — one User has many Tickets (through Bookings).
- `notifications` — one User has many Notifications.
- `reward_transactions` — one User has many RewardTransactions.
- `promo_code_usages` — one User has many PromoCodeUsages.
- `reschedule_requests` — one User (admin) has many EventReschedules.
- `uploaded_files` — one User has many UploadedFiles.
- `email_logs` — one User has many EmailLogs.

**Business rules:**
- Email must be unique and is used for login.
- Password is stored as a hash, never as plain text.
- `reward_balance` starts at 0 and is changed only through RewardTransaction records.
- `is_active = False` should block login and bookings.

---

## 2. Category

**What it represents:** a grouping for events (e.g. Concert, Theater, Sports). This lets
customers browse events by type. It is the simplest model in the system.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `name` | String(100) | | NN | ✅ | | — | e.g. "Concert" |
| `description` | Text | | nullable | | | — | **Proposal** |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Relationships:**
- `events` — one Category has many Events.

**Business rules:** category names are unique. Deleting a category with events — **To be decided**.

---

## 3. Venue

**What it represents:** a physical location where events are held. It already exists as
a plain Python placeholder class (`models/venue.py`) and must be converted into a real
SQLAlchemy model.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `name` | String(100) | | NN | | | — | |
| `address` | String(255) | | nullable | | | — | required or not — **To be decided** |
| `capacity` | Integer | | NN | | `0` | — | total capacity |
| `is_active` | Boolean | | NN | | `True` | — | **Proposal** |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Relationships:**
- `events` — one Venue has many Events.
- `seats` — one Venue has many Seats (if seats belong to the venue — see Seat design note).

**Business rules:** a seated event must not exceed the venue capacity.

---

## 4. Event

**What it represents:** a single scheduled event that customers can buy tickets for.
Already exists as a plain Python placeholder class (`models/event.py`) and must be
converted into a real SQLAlchemy model.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `category_id` | Integer | | NN | | | `category.id` | |
| `venue_id` | Integer | | NN | | | `venue.id` | |
| `title` | String(150) | | NN | | | — | |
| `description` | Text | | nullable | | | — | |
| `event_date` | DateTime | | NN | | | — | drives seat-hold expiry and ticket expiry |
| `event_type` | String(20) | | NN | | `"seated"` | — | `seated` / `general_admission` — see Part G |
| `status` | String(20) | | NN | | `"unpublished"` | — | see enum below |
| `ticket_price` | Numeric(10,2) | | NN | | `0` | — | base price; used mainly by general-admission events |
| `capacity` | Integer | | nullable | | | — | max tickets for GA events; **To be decided** |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Enums / status values (`status`):** `published`, `unpublished` (Strictly binary event status system).

**Relationships:**
- `category` — many Events belong to one Category.
- `venue` — many Events belong to one Venue.
- `seats` — one Event has many Seats.
- `addons` — one Event has many EventAddons.
- `bookings` — one Event has many Bookings.
- `seat_holds` — one Event has many SeatHolds.
- `reschedules` — one Event has many EventReschedules.
- `tickets` — one Event has many Tickets (through Bookings).

**Business rules:**
- `event_date` must be in the future when the event is published.
- `rescheduled` status is applied together with an EventReschedule record (see Part E).
- Tickets become `EXPIRED` relative to `event_date` (see Part D).

---

## 5. Seat

**What it represents:** one specific bookable seat. It marks the concrete difference
between "seated" events (customer picks a seat) and "general admission" events
(customer picks a quantity — no seats involved).

> **Design decision — "To be decided" during review:** seats may belong to the **Event**
> (each event creates its own seat layout) or to the **Venue** (shared layout reused by
> every event at that venue).
> **Proposal:** seats belong to the **Event**. This keeps hold/availability logic simple
> (each event has its own seat rows) and is the easiest to implement and reason about.
> The downside (duplicated layout for repeat events) is acceptable for this project.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `event_id` | Integer | | NN | | | `event.id` | per the proposal above |
| `row` | String(10) | | NN | | | — | e.g. "A"; **Proposal** |
| `number` | String(10) | | NN | | | — | e.g. "12"; **Proposal** |
| `section` | String(50) | | nullable | | | — | e.g. "VIP"; **Proposal** |
| `price` | Numeric(10,2) | | NN | | `0` | — | per-seat price; **Proposal** |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Enums / status values:** none — a seat's availability is **derived**, not stored.
A seat is:
- `available` when it has no active SeatHold and no confirmed BookingItem;
- `held` when an active SeatHold references it;
- `sold` when a BookingItem in a confirmed booking references it.

**Relationships:**
- `event` — many Seats belong to one Event.
- `holds` — one Seat has many SeatHolds (only one active at a time).
- `booking_items` — one Seat has many BookingItems (only one per confirmed booking).
- `tickets` — one Seat has many Tickets (through BookingItems).

**Business rules:**
- A seat can never have more than one **active** SeatHold at the same time.
- A seat can never be part of two **confirmed** bookings at the same time.
- (Unique `event_id` + `row` + `number` is recommended to prevent duplicate seats — **Proposal**.)

---

## 6. EventAddon

**What it represents:** an optional extra that a customer can add to a booking for a
specific event (e.g. VIP parking, merchandise bundle, insurance).

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `event_id` | Integer | | NN | | | `event.id` | |
| `name` | String(100) | | NN | | | — | |
| `description` | Text | | nullable | | | — | |
| `price` | Numeric(10,2) | | NN | | `0` | — | |
| `is_active` | Boolean | | NN | | `True` | — | |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Relationships:**
- `event` — many EventAddons belong to one Event.
- `booking_addons` — one EventAddon has many BookingAddons.

**Business rules:** only `is_active` addons may be added to a new booking. Price is
snapshotted into BookingAddon at purchase time (later price changes must not affect
existing bookings).

---

## 7. SeatHold

**What it represents:** a temporary lock placed on a seat for one customer while they
check out. This is the mechanism behind the **1-minute temporary hold** (see Part C).

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | NN | | | `user.id` | who holds the seat |
| `event_id` | Integer | | NN | | | `event.id` | |
| `seat_id` | Integer | | NN | | | `seat.id` | |
| `booking_id` | Integer | | nullable | | | `booking.id` | set when the hold becomes a booking |
| `status` | String(20) | | NN | | `"held"` | — | see enum below |
| `held_at` | DateTime | | NN | | `utcnow` | — | |
| `expires_at` | DateTime | | NN | | — | — | `held_at` + 1 minute |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Enums / status values (`status`):**
- `held` — the seat is locked for this user.
- `converted` — the hold was turned into a Booking (booking_id set).
- `released` — the user cancelled; seat freed immediately.
- `expired` — the hold outlived `expires_at`; seat freed.

**Relationships:**
- `user` — many SeatHolds belong to one User.
- `event` — many SeatHolds belong to one Event.
- `seat` — many SeatHolds belong to one Seat.
- `booking` — one SeatHold may become one Booking.

**Business rules:**
- A seat is unavailable to other customers while it has a `held` hold that has not
  expired (compared against `expires_at`).
- When a hold expires or is released, its seat becomes available again immediately.
- At most one active hold per (event, seat) — enforced in the booking service later.
- One hold row = one seat (holds are per-seat, not per-quantity).

---

## 8. Booking

**What it represents:** the order a customer places for an event. It is the central
document of the system: everything (items, add-ons, promo, cashback, tickets,
notifications) hangs off it. Currently a plain Python placeholder class
(`models/booking.py`) that must be converted into a real SQLAlchemy model.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | NN | | | `user.id` | |
| `event_id` | Integer | | NN | | | `event.id` | |
| `promo_code_id` | Integer | | nullable | | | `promo_code.id` | set when a promo is applied |
| `booking_reference` | String(32) | | NN | ✅ | — | — | human-friendly order number |
| `status` | String(20) | | NN | | `"pending"` | — | see enum below |
| `subtotal` | Numeric(10,2) | | NN | | `0` | — | sum of items + add-ons before promo |
| `discount_amount` | Numeric(10,2) | | NN | | `0` | — | promo discount applied |
| `total_amount` | Numeric(10,2) | | NN | | `0` | — | subtotal − discount |
| `cashback_amount` | Numeric(10,2) | | NN | | `0` | — | 2% of total (see Part F) |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Enums / status values (`status`):** `pending`, `confirmed`, `cancelled` (required);
`completed`, `expired`, `refunded` — **To be decided**.

**Relationships:**
- `user` — many Bookings belong to one User.
- `event` — many Bookings belong to one Event.
- `promo_code` — many Bookings may use one PromoCode.
- `items` — one Booking has many BookingItems.
- `addons` — one Booking has many BookingAddons.
- `tickets` — one Booking has many Tickets.
- `seat_holds` — one Booking may have been created from one or more SeatHolds.
- `promo_code_usage` — one Booking creates at most one PromoCodeUsage.
- `reward_transactions` — one Booking may create one RewardTransaction (cashback).
- `email_logs` — one Booking may have many EmailLogs.

**Business rules:**
- `booking_reference` is unique and auto-generated (e.g. `SMU` + timestamp/random).
- Amounts are snapshots: once the booking exists, item/add-on price changes do not alter it.
- A booking is created from active SeatHolds; holds are marked `converted` at that moment.
- Cancelling a booking must release its seats and mark its tickets `CANCELLED`.

---

## 9. BookingItem

**What it represents:** one line in a booking. For seated events, one line = one seat.
For general-admission events, one line = a quantity of admission tickets.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `booking_id` | Integer | | NN | | | `booking.id` | |
| `seat_id` | Integer | | nullable | | | `seat.id` | **null for general admission** |
| `quantity` | Integer | | NN | | `1` | — | GA events use quantity; seated events use `1` |
| `unit_price` | Numeric(10,2) | | NN | | `0` | — | price snapshot at purchase |

**Relationships:**
- `booking` — many BookingItems belong to one Booking.
- `seat` — one BookingItem may reference one Seat (null for GA).
- `ticket` — one BookingItem has one or more Tickets (one per quantity unit).

**Business rules:**
- For seated events: `quantity = 1` and `seat_id` is required.
- For general-admission events: `seat_id = NULL` and `quantity >= 1`.
- The same seat may appear in at most one **confirmed** booking.

---

## 10. BookingAddon

**What it represents:** one add-on line chosen during checkout (ties a Booking to an
EventAddon with the price at purchase time).

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `booking_id` | Integer | | NN | | | `booking.id` | |
| `addon_id` | Integer | | NN | | | `event_addon.id` | |
| `quantity` | Integer | | NN | | `1` | — | |
| `unit_price` | Numeric(10,2) | | NN | | `0` | — | price snapshot at purchase |

**Relationships:**
- `booking` — many BookingAddons belong to one Booking.
- `addon` — many BookingAddons reference one EventAddon.

**Business rules:** price is snapshotted at checkout, so later EventAddon price edits
do not change existing bookings.

---

## 11. PromoCode

**What it represents:** a discount code (e.g. `WELCOME10`) that customers can apply to
a booking.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `code` | String(50) | | NN | ✅ | | — | shown to customers |
| `description` | String(255) | | nullable | | | — | |
| `discount_type` | String(20) | | NN | | `"percentage"` | — | `percentage` / `fixed` |
| `discount_value` | Numeric(10,2) | | NN | | | — | e.g. 10 (for 10%) or 5.00 (fixed) |
| `max_uses` | Integer | | nullable | | | — | `NULL` = unlimited |
| `used_count` | Integer | | NN | | `0` | — | incremented on each use |
| `valid_from` | DateTime | | nullable | | | — | promo not usable before this |
| `valid_until` | DateTime | | nullable | | | — | promo not usable after this |
| `is_active` | Boolean | | NN | | `True` | — | manual on/off switch |
| `created_at` | DateTime | | NN | | `utcnow` | — | |
| `updated_at` | DateTime | | NN | | `utcnow` (onupdate) | — | |

**Relationships:**
- `bookings` — one PromoCode can be used by many Bookings.
- `usages` — one PromoCode has many PromoCodeUsages.

**Business rules:**
- A code is usable only if `is_active`, within `valid_from`/`valid_until`, and
  `used_count < max_uses` (when `max_uses` is set).
- One-use-per-user limit — **To be decided** (a unique `(promo_code_id, user_id)`
  constraint on PromoCodeUsage would enforce it).

---

## 12. PromoCodeUsage

**What it represents:** a record of one promo code being used by one user on one booking
(audit trail for the promo system).

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `promo_code_id` | Integer | | NN | | | `promo_code.id` | |
| `user_id` | Integer | | NN | | | `user.id` | |
| `booking_id` | Integer | | NN | | | `booking.id` | |
| `used_at` | DateTime | | NN | | `utcnow` | — | |

**Relationships:**
- `promo_code` — many usages belong to one PromoCode.
- `user` — many usages belong to one User.
- `booking` — one usage belongs to one Booking.

**Business rules:**
- Created atomically when the booking is confirmed (same transaction), so `used_count`
  and the usage record never drift apart.
- Optional unique constraint `(promo_code_id, user_id)` if codes are one-per-user.

---

## 13. RewardTransaction

**What it represents:** every change to a user's `reward_balance` — crediting the
planned **2% cashback** on completed bookings and any future debits/spends.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | NN | | | `user.id` | |
| `booking_id` | Integer | | nullable | | | `booking.id` | set for booking cashback |
| `type` | String(20) | | NN | | | — | `credit` / `debit` |
| `amount` | Integer | | NN | | | — | whole points — matches Integer `reward_balance` |
| `balance_after` | Integer | | NN | | | — | user balance snapshot after this entry |
| `description` | String(255) | | nullable | | | — | e.g. "2% cashback — booking SMU..." |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Relationships:**
- `user` — many RewardTransactions belong to one User.
- `booking` — many RewardTransactions may reference one Booking.

**Business rules:**
- Cashback = 2% of booking `total_amount`, **rounded** to a whole point (Integer) —
  rounding rule **To be decided** (floor / round).
- `balance_after` stores the running balance so history is auditable without recomputation.
- `reward_balance` is updated in the same transaction as the RewardTransaction insert.

---

## 14. Notification

**What it represents:** an in-app message for a user (booking confirmed, ticket ready,
event rescheduled, cashback credited, etc.).

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | NN | | | `user.id` | |
| `type` | String(30) | | NN | | `"info"` | — | see enum below |
| `title` | String(150) | | NN | | | — | **Proposal** |
| `message` | Text | | NN | | | — | |
| `is_read` | Boolean | | NN | | `False` | — | |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Enums / status values (`type`):** `booking`, `ticket`, `reschedule`, `reward`,
`system`, `info` (**Proposal**).

**Relationships:**
- `user` — many Notifications belong to one User.

**Business rules:**
- Notifications are written in the same flow that creates the event they describe
  (booking confirmation, reschedule, cashback).
- Email sending is a **separate** concern handled by EmailLog (Part H) — Notification is
  the in-app channel, EmailLog is the email channel.

---

## 15. Ticket

**What it represents:** the actual admission entitlement a customer gets after a
confirmed booking — one Ticket per seat (seated events) or per quantity unit
(general-admission events). Carries a QR code for verification.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `booking_id` | Integer | | NN | | | `booking.id` | |
| `booking_item_id` | Integer | | NN | | | `booking_item.id` | ticket always belongs to a booking line |
| `seat_id` | Integer | | nullable | | | `seat.id` | set for seated events, null for GA |
| `event_id` | Integer | | NN | | | `event.id` | denormalized convenience for expiry + verification; **Proposal** |
| `qr_code` | String(255) | | NN | ✅ | — | — | unique token rendered as QR |
| `status` | String(20) | | NN | | `"valid"` | — | see Part D |
| `issued_at` | DateTime | | NN | | `utcnow` | — | |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Enums / status values (`status`):** `valid`, `used`, `cancelled`, `expired` — see Part D.

**Relationships:**
- `booking` — many Tickets belong to one Booking.
- `booking_item` — many Tickets belong to one BookingItem.
- `seat` — many Tickets may reference one Seat.
- `event` — many Tickets reference one Event (via `event_id`).
- `verifications` — one Ticket has many TicketVerifications (scan history).

**Business rules:**
- Tickets are created only for `confirmed` bookings.
- One Ticket per seat (seated) or per quantity unit (GA).
- `qr_code` is unique — it is what the door scanner checks.
- Ticket lifecycle transitions are documented in Part D.

---

## 16. TicketVerification

**What it represents:** one scan of a ticket QR code at the venue entrance. Each scan
is recorded so entry attempts are auditable.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `ticket_id` | Integer | | NN | | | `ticket.id` | |
| `verifier_user_id` | Integer | | nullable | | | `user.id` | which admin/user scanned; guest scanning — **To be decided** |
| `result` | String(20) | | NN | | | — | see enum below |
| `notes` | String(255) | | nullable | | | — | e.g. "QR damaged" |
| `verified_at` | DateTime | | NN | | `utcnow` | — | |

**Enums / status values (`result`):** `valid` (first scan of a valid ticket),
`already_used` (re-scan), `expired` (past event date), `invalid` (unknown/cancelled QR).

**Relationships:**
- `ticket` — many verifications belong to one Ticket.
- `verifier` — many verifications may belong to one User (admin).

**Business rules:**
- A scan may be recorded even when it fails (`already_used`, `expired`, `invalid`) — every
  attempt is logged.
- Successfully verifying a ticket sets the ticket status to `used`.

---

## 17. EventReschedule

**What it represents:** a record of an event date being changed by an admin, including
the old and new dates. Supports the reschedule flow in Part E.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `event_id` | Integer | | NN | | | `event.id` | |
| `user_id` | Integer | | NN | | | `user.id` | the admin who performed the change |
| `old_date` | DateTime | | NN | | | — | event date before change |
| `new_date` | DateTime | | NN | | | — | event date after change |
| `reason` | Text | | nullable | | | — | **Proposal** |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Relationships:**
- `event` — many reschedules belong to one Event.
- `user` — many reschedules are performed by one User (admin).

**Business rules:**
- **Password confirmation is an application-level requirement:** the admin must
  re-enter their password before the reschedule is saved (enforced in the controller /
  service layer, not by the model).
- Every reschedule appends a new EventReschedule row; the event's `event_date` is updated
  and its status becomes `rescheduled`.
- `new_date` must be in the future.

---

## 18. UploadedFile

**What it represents:** a record of any file uploaded to the system (event images,
venue images, user ID documents). The file itself is stored on disk / in `static/uploads`;
the model stores its metadata.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | nullable | | | `user.id` | uploader (null for anonymous) |
| `event_id` | Integer | | nullable | | | `event.id` | file attached to an event |
| `venue_id` | Integer | | nullable | | | `venue.id` | file attached to a venue |
| `purpose` | String(30) | | nullable | | | — | e.g. `event_image`, `id_document`, `profile` — **To be decided** |
| `original_filename` | String(255) | | NN | | | — | name on uploader's machine |
| `stored_path` | String(255) | | NN | ✅ | — | — | where the file actually lives |
| `mime_type` | String(100) | | nullable | | | — | |
| `size` | Integer | | NN | | `0` | — | bytes |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Relationships:**
- `user` — many UploadedFiles may belong to one User.
- `event` — many UploadedFiles may belong to one Event.
- `venue` — many UploadedFiles may belong to one Venue.

**Business rules:**
- `stored_path` must be unique — the file name is generated by the app, never trusted
  from the client.
- Whether one file can be attached to multiple targets (user AND event) — **To be decided**.

---

## 19. EmailLog

**What it represents:** an audit record for every email the system sends (booking
confirmation, tickets, reschedule notices, password reset). Keeps email delivery
observable even when a mail provider is not configured yet.

| Field | Type | PK | Nullable | Unique | Default | FK | Notes |
| --- | --- | :-: | :-: | :-: | --- | --- | --- |
| `id` | Integer | ✅ | — | — | auto | — | |
| `user_id` | Integer | | nullable | | | `user.id` | recipient user (null for non-user recipients) |
| `booking_id` | Integer | | nullable | | | `booking.id` | linked booking, when applicable |
| `recipient_email` | String(255) | | NN | | | — | to address |
| `subject` | String(255) | | NN | | | — | |
| `body` | Text | | NN | | | — | rendered content |
| `template_name` | String(100) | | nullable | | | — | which template produced it |
| `status` | String(20) | | NN | | `"pending"` | — | `pending` / `sent` / `failed` |
| `error_message` | Text | | nullable | | | — | provider error on failure |
| `sent_at` | DateTime | | nullable | | | — | set when delivered |
| `created_at` | DateTime | | NN | | `utcnow` | — | |

**Relationships:**
- `user` — many EmailLogs may belong to one User.
- `booking` — many EmailLogs may belong to one Booking.

**Business rules:**
- A log row is created before sending; `status` is updated to `sent` or `failed` after.
- Email is non-blocking for the booking flow (a failed email never rolls back a booking).

---

# Part B — Model relationship overview

```
Category ──1:N──> Event ──1:N──> Seat
Venue    ──1:N──> Event ──1:N──> EventAddon
Event    ──1:N──> Booking
Event    ──1:N──> SeatHold
Event    ──1:N──> EventReschedule

User ──1:N──> Booking ──1:N──> BookingItem ──1:N──> Ticket ──1:N──> TicketVerification
User ──1:N──> Booking       │
User ──1:N──> SeatHold      ├──1:N──> BookingAddon ──N:1──> EventAddon
User ──1:N──> Notification  ├──1:1──> PromoCodeUsage ──N:1──> PromoCode
User ──1:N──> RewardTransaction └──1:N──> EmailLog
User ──1:N──> PromoCodeUsage
User ──1:N──> UploadedFile
User ──1:N──> EventReschedule (admin)
User ──1:N──> TicketVerification (verifier)
```

Full chain for one completed purchase:

```
User
 └── Booking
      ├── BookingItem ──> Seat (seated) | quantity (general admission)
      │      └── Ticket ──> TicketVerification
      ├── BookingAddon ──> EventAddon
      ├── PromoCodeUsage ──> PromoCode
      ├── RewardTransaction (2% cashback)
      ├── EmailLog
      └── SeatHold (the holds that created it)
```

Summary of ownership:

| Model | Belongs to | Owns |
| --- | --- | --- |
| User | — | Booking, SeatHold, Notification, RewardTransaction, PromoCodeUsage, UploadedFile, EmailLog, EventReschedule, TicketVerification |
| Category | — | Event |
| Venue | — | Event |
| Event | Category, Venue | Seat, EventAddon, Booking, SeatHold, EventReschedule |
| Seat | Event | SeatHold, BookingItem, Ticket |
| EventAddon | Event | BookingAddon |
| Booking | User, Event | BookingItem, BookingAddon, Ticket, EmailLog |
| PromoCode | — | Booking, PromoCodeUsage |
| Ticket | Booking, BookingItem, Event | TicketVerification |

---

# Part C — Seat-hold logic (1-minute temporary hold)

**Models involved:** `Event`, `Seat`, `User`, `SeatHold`, `Booking`

```
Customer opens an event page
        │
        ▼
Customer selects a seat ──> SeatHold created (status=held, expires_at = now + 60s)
        │                     seat is now unavailable to everyone else
        ▼
Customer checks out within 60 seconds
        │
        ├── SUCCESS: Booking created (confirmed)
        │            holds → status=converted, booking_id set
        │            seats locked permanently via BookingItem
        │
        └── TIMEOUT / CANCEL:
             holds expire (lazy check on next query) or are released
             seats become available again
```

**How it works:**

1. One `SeatHold` row per (event, seat, user). A seat is shown as taken while any
   `held` hold exists whose `expires_at` is still in the future.
2. `expires_at = held_at + 60 seconds` (the 1-minute hold).
3. Expiry is checked **lazily**: before a seat is sold, the app queries for active
   holds; expired ones are flagged `expired` and ignored. A background cleanup job is
   optional — **To be decided**.
4. On successful checkout, the holds become `converted` and point at the new Booking.
   The BookingItems now own the seats.
5. If the user abandons checkout or times out, the seat automatically becomes available
   again — no manual action needed.

**Business rules:**
- A seat can have at most one active (non-expired, non-released) hold at a time.
- Holds are per-seat. General-admission events use quantity, so they do **not** need
  holds in the same way — quantity reservation is handled at booking time
  (**To be decided**: whether GA events need a simple quantity hold).

---

# Part D — Ticket lifecycle

**Models involved:** `Ticket`, `TicketVerification`, `Event`

A ticket moves through exactly these states:

```
                 confirmed booking
                        │
                        ▼
   ┌────────── VALID ◄────┘  (default — ticket is live, QR scannable)
   │
   ├── first successful scan ──► USED       (entered the venue)
   │
   ├── booking cancelled ──────► CANCELLED  (no longer valid, QR must be rejected)
   │
   └── event date passed ──────► EXPIRED    (never scanned, now worthless)
```

| State | Meaning | Set by |
| --- | --- | --- |
| `VALID` | Ticket is usable. | created with the confirmed booking |
| `USED` | Entry was granted; scanned once successfully. | first `TicketVerification` with result `valid` |
| `CANCELLED` | Booking was cancelled; ticket cannot be used. | booking cancellation |
| `EXPIRED` | Event date/time has passed and the ticket was never used. | check against `event.event_date` |

**Expiry rule:** a `VALID` ticket automatically becomes `EXPIRED` once the event's
`event_date` (+ duration, if any — **To be decided**) has passed. Expiry depends on the
**event date/time**, not on when the ticket was issued. It can be evaluated lazily at
scan time (`if now > event.event_date → EXPIRED`) and/or stored on the ticket during a
cleanup job — implementation detail, not a separate model.

**Verification:** each scan creates a `TicketVerification` with a `result`
(`valid` / `already_used` / `expired` / `invalid`). Only a `VALID` ticket scans as
`valid`, and that scan flips it to `USED`.

---

# Part E — Event rescheduling

**Models involved:** `Event`, `EventReschedule`, `Ticket`, `Notification`, `User`

```
Admin (User, role=admin) requests to reschedule an event
        │
        ├── REQUIRED: admin re-enters their password (application-level confirmation)
        │              — reschedule is REFUSED if the password does not match
        ▼
EventReschedule row created (old_date, new_date, user_id, reason)
        │
        ▼
Event.event_date = new_date
Event.status     = rescheduled
        │
        ├──► Notification created for every user with tickets for this event
        │       (type = reschedule)
        ├──► EmailLog rows queued for the same users (reschedule notice)
        └──► Existing VALID tickets are NOT deleted — they stay VALID and remain
              scannable at the new date. Ticket expiry now follows the new event_date.
```

**Business rules:**
- **Password confirmation happens at the application level** (controller/service),
  before the new EventReschedule row is written. It is not a database concern.
- The full reschedule (new EventReschedule + Event.date update + status change) happens
  in one database transaction.
- Tickets are unaffected in status — only their effective expiry window moves.
- Affected users are the ones with confirmed bookings/tickets for that event
  (found via Booking → Ticket).

---

# Part F — Promo code and reward (2% cashback) system

**Models involved:** `PromoCode`, `PromoCodeUsage`, `RewardTransaction`, `User`, `Booking`

```
Customer applies a PromoCode at checkout
        │
        ▼
Validation (active, within dates, uses remaining)
        │
        ▼
Booking created (confirmed)
   ├── discount_amount = promo discount
   ├── total_amount    = subtotal − discount
   └── promo_code_id   = applied code
        │
        ▼
PromoCodeUsage created (promo_code, user, booking) + used_count += 1
        │
        ▼
Cashback: amount = 2% of booking total_amount (rounded to whole points)
        │
        ├── RewardTransaction created (type=credit, booking_id, balance_after)
        └── User.reward_balance += amount      (same transaction)
```

**Business rules:**
- 2% cashback is calculated on the **paid total** (`total_amount`, after promo
  discount) — exact base **To be decided**.
- Cashback is issued when the booking is confirmed, not at checkout entry.
- `reward_balance` and the RewardTransaction are written in the **same transaction**.
- PromoCodeUsage prevents double-counting: one booking = at most one usage row.
- Reward points are Integers (matches `reward_balance`), so fractional cashback must be
  rounded — rounding rule **To be decided**.

---

# Part G — General admission vs seated events

One architecture serves both — no second code path in the data model.

`Event.event_type` decides which flow applies:

| Aspect | `seated` (default) | `general_admission` |
| --- | --- | --- |
| Customer picks | a specific Seat | a **quantity** |
| Seat records | created for the event | **none created** |
| BookingItem | `seat_id` set, `quantity = 1` | `seat_id = NULL`, `quantity = n` |
| SeatHold | one hold per seat | not needed (quantity reserved at checkout) |
| Ticket | one per seat | one per quantity unit (`quantity` tickets) |

```
Seated:   Event ──> Seat ──> SeatHold/BookingItem ──> Ticket
GA:       Event ──> BookingItem (quantity, no seat) ──> Ticket × quantity
```

- The **same** `Booking`, `BookingItem`, `Ticket`, and `Verification` models serve both
  modes — only the `seat_id` / `quantity` combination differs.
- GA events may still need a `capacity` cap (Event.capacity) — **To be decided**.

---

# Part H — File and email handling

**UploadedFile** — one row per uploaded file (metadata only). Files live in
`static/uploads/`. It is referenced by users (ID documents), events, and venues
(images). The app generates the stored filename; `stored_path` is unique. Serving files
is a controller concern (outside this blueprint).

**EmailLog** — one row per outbound email, written **before** sending and updated to
`sent` / `failed` after. Its purpose is auditability: which user, which booking, which
template, which error — without depending on any email provider being configured. It is
the email counterpart of `Notification` (in-app) — both are typically created in the
same business flow.

---

# Part I — Recommended implementation order

Beginner-friendly order. The rule behind it: **implement models from the "outside in" —
first the ones nothing else references, then the ones that depend on them.** Every model
imports only models that already exist, so `models/__init__.py` grows without circular
imports, and each model can be created and tested on its own.

| # | Model | Why here |
| --- | --- | --- |
| 1 | **User** | ✅ already implemented. Everything references it — start by reviewing it. |
| 2 | **Category** | Tiny, standalone, no foreign keys. Easy first win. |
| 3 | **Venue** | Standalone; Events depend on it. |
| 4 | **Event** | Depends on Category + Venue; almost every later model depends on it. |
| 5 | **Seat** | Depends only on Event. |
| 6 | **EventAddon** | Depends only on Event. |
| 7 | **PromoCode** | Standalone, needed by Booking (referenced as a FK). |
| 8 | **Booking** | The hub: depends on User, Event, PromoCode. |
| 9 | **BookingItem** | Depends on Booking + Seat. |
| 10 | **BookingAddon** | Depends on Booking + EventAddon. |
| 11 | **SeatHold** | Depends on User, Event, Seat, Booking — simplest after the booking chain exists. |
| 12 | **Ticket** | Depends on Booking + BookingItem. |
| 13 | **TicketVerification** | Depends only on Ticket. |
| 14 | **EventReschedule** | Depends on Event + User. |
| 15 | **PromoCodeUsage** | Depends on PromoCode + User + Booking. |
| 16 | **RewardTransaction** | Depends on User + Booking (cashback is applied after booking exists). |
| 17 | **Notification** | Depends only on User; fits after the flows that produce it (booking, reschedule, reward). |
| 18 | **UploadedFile** | Largely standalone; only referenced by controllers. |
| 19 | **EmailLog** | Largely standalone; fits last or together with Notification. |

**Why this order is beginner-friendly:**

- Early models are small and have **no foreign keys**, so they can be created and tested
  in isolation.
- Each later model imports **only already-existing models** — no circular imports, no
  forward references.
- The booking chain (8–13) is built in the same order it is used at runtime:
  hold → booking → items → tickets → verification.
- The cashback/promo pair (7, 15, 16) is deferred until the booking chain proves correct.
- Utility models (17–19) come last because they only make sense once the flows that
  trigger them exist.

---

## Open questions (consolidated "To be decided" list)

1. `Seat`: belongs to Event or Venue? (Proposal: Event.)
2. `Event.status` and `Booking.status` full enum lists.
3. Promo code: one-use-per-user limit? (Unique `(promo_code_id, user_id)`.)
4. Cashback rounding rule (floor vs round) for 2% of total.
5. GA events: quantity hold + capacity cap needed?
6. `Venue.address` / `UploadedFile.purpose` / `Event.capacity` required or not.
7. Ticket expiry: stored column vs lazy check at scan time.
8. Extra user roles (venue manager) beyond `customer` / `admin`.
