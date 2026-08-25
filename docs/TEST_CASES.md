# SeatMeUp — Comprehensive Test Cases & QA Specification

This document details the test matrix, test cases, preconditions, execution steps, expected outcomes, and actual validation results for the **SeatMeUp** smart ticketing platform.

All test suites run in CI/CD and local environments via `pytest` (`186 passed (SQLite in-memory test DB), 3 passed (Live MySQL integration test DB)` — **189 total tests**).

---

## Test Summary Matrix

| Module | Test Case ID | Test Type | Scenario | Expected Result | Status |
|---|---|---|---|---|---|
| **AUTH** | `TC-AUTH-001` | Unit / Controller | User registration with strong password | User created, password hashed with PBKDF2/scrypt, HTTP 201 | **PASS** |
| **AUTH** | `TC-AUTH-002` | Unit / Controller | Duplicate email registration | Rejection with HTTP 409 / error flash | **PASS** |
| **AUTH** | `TC-AUTH-003` | Unit / Integration | JWT Login with valid credentials | Access token + Refresh token issued, HTTP 200 | **PASS** |
| **AUTH** | `TC-AUTH-004` | Unit / Integration | Login with invalid password | Rejection with HTTP 401 Unauthorized | **PASS** |
| **RBAC** | `TC-RBAC-001` | Integration | Customer accesses `/api/admin/events` | Forbidden with HTTP 403 / redirect | **PASS** |
| **RBAC** | `TC-RBAC-002` | Integration | Admin accesses `/admin/dashboard` & `/admin/events` | Full access granted with HTTP 200 | **PASS** |
| **CSRF** | `TC-CSRF-001` | Integration | Web form POST without CSRF token | Blocked with HTTP 400 Bad Request | **PASS** |
| **CSRF** | `TC-CSRF-002` | Integration | Web form POST with valid CSRF token | Processed successfully with HTTP 200/302 | **PASS** |
| **CSRF** | `TC-CSRF-003` | Integration | API endpoint with `Authorization: Bearer <token>` | Exemption from CSRF check, HTTP 200/201 | **PASS** |
| **EVENTS** | `TC-EVT-001` | Unit / Controller | Admin creates new event (Title, Venue, Date, Price) | Event stored in DB with default status, HTTP 201 | **PASS** |
| **EVENTS** | `TC-EVT-002` | Unit / Integration | Public user views published events | List of available events returned, HTTP 200 | **PASS** |
| **EVENTS** | `TC-EVT-003` | Unit / Controller | Public user attempts to view unpublished event | Filtered out from public query, HTTP 404 | **PASS** |
| **VENUES** | `TC-VEN-001` | Unit / Controller | Admin creates venue with capacity | Venue persisted with address, type, capacity, HTTP 201 | **PASS** |
| **SEATS** | `TC-SET-001` | Unit / Service | Bulk seat grid generator (Rows A-E, Seats 1-10) | 50 unique seats generated and linked to venue | **PASS** |
| **SEATS** | `TC-SET-002` | Unit / Integration | Customer holds seat for 60 seconds | Seat status changes to `held`, expiration timestamp set, HTTP 201 | **PASS** |
| **SEATS** | `TC-SET-003` | Integration | Second user attempts to hold same held seat | Conflict detected, rejected with HTTP 409 | **PASS** |
| **SEATS** | `TC-SET-004` | Unit / Service | Hold expires after TTL (60s) | Seat automatically becomes `available` for other users | **PASS** |
| **BOOKING** | `TC-BKG-001` | Unit / Integration | Confirm booking for held seats with add-ons | Booking confirmed, reference generated, seats booked, HTTP 201 | **PASS** |
| **BOOKING** | `TC-BKG-002` | Unit / Integration | General Admission booking with ticket quantity | Capacity decremented, booking items created, HTTP 201 | **PASS** |
| **BOOKING** | `TC-BKG-003` | Integration | Customer cancels booking | Booking marked `cancelled`, seats released, cashback deducted | **PASS** |
| **IDEMP** | `TC-IDEMP-001`| Unit / Service | Duplicate checkout request with same `Idempotency-Key` | Original booking safely replayed without duplicate seats or charges | **PASS** |
| **IDEMP** | `TC-IDEMP-002`| Unit / Service | Replay prevents double cashback credit & double promo increment | Wallet balance & promo usage count remain strictly single-count | **PASS** |
| **IDEMP** | `TC-IDEMP-003`| Unit / Service | Idempotency key from another user rejected | HTTP 403 Forbidden | **PASS** |
| **OPERATIONS**| `TC-OPS-001` | Unit / Service | Event Operations Dashboard (Capacity, Sold, Check-ins) | Sales occupancy, live occupancy, no-shows computed accurately | **PASS** |
| **OPERATIONS**| `TC-OPS-002` | Unit / Service | Transparent Rule-Based Event Health Score (0-100) | Metric points computed with human-readable reason audit trail | **PASS** |
| **PROMOS** | `TC-PRM-001` | Unit / Service | Percentage promo code application (`WELCOME10` - 10%) | 10% calculated from subtotal and deducted | **PASS** |
| **PROMOS** | `TC-PRM-002` | Unit / Service | Fixed amount promo code (`SAVE200` - ₹200 on min ₹1000) | Fixed ₹200 deducted when subtotal >= ₹1000 | **PASS** |
| **PROMOS** | `TC-PRM-003` | Unit / Service | Min spend not met (`SAVE200` with ₹500 order) | Promo rejected with descriptive minimum spend error | **PASS** |
| **PROMOS** | `TC-PRM-004` | Unit / Service | Expired promo code application (`EXPIRED50`) | Promo rejected with "Code has expired" message | **PASS** |
| **PROMOS** | `TC-PRM-005` | Unit / Service | Inactive/Deactivated promo code (`INACTIVE20`) | Promo rejected with "Invalid or inactive promo code" | **PASS** |
| **PROMOS** | `TC-PRM-006` | Unit / Service | Promo max usage limit reached (`MAXED100`) | Promo rejected once usage count >= max_uses | **PASS** |
| **REWARDS** | `TC-RWD-001` | Unit / Service | 2% Cashback calculation on confirmed booking | Exactly 2% of final total credited to user wallet balance | **PASS** |
| **REWARDS** | `TC-RWD-002` | Unit / Service | Cashback deduction on booking cancellation | Cashback deducted, ledger transaction recorded | **PASS** |
| **TICKETS** | `TC-TCK-001` | Unit / Service | Ticket QR token generation | Unique secure UUID token generated and mapped to booking | **PASS** |
| **TICKETS** | `TC-TCK-002` | Unit / Integration | Door entrance staff scans valid ticket (`/verify/<token>`) | Verification succeeds, status updated from `valid` to `used`, HTTP 200 | **PASS** |
| **TICKETS** | `TC-TCK-003` | Integration | Double scan prevention (Scanning already used ticket) | Verification rejected with HTTP 409 Conflict / "Already used" | **PASS** |
| **TICKETS** | `TC-TCK-004` | Unit / Controller | PDF Ticket Download (`/bookings/<ref>/ticket/pdf`) | Dynamic PDF generated with ReportLab / fallback header, HTTP 200 | **PASS** |
| **RESCHED** | `TC-RSC-001` | Unit / Service | Admin reschedules event date/time with password check | Event updated, audit row created, notification dispatched | **PASS** |
| **FILES** | `TC-FIL-001` | Unit / Service | Upload event poster image (JPEG/PNG, <=5MB) | Validated, unique filename created, saved to `/uploads` | **PASS** |
| **FILES** | `TC-FIL-002` | Unit / Service | Upload invalid file type (`.exe` / `.sh`) | Rejected by whitelist validation with descriptive error | **PASS** |
| **ANALYTICS**| `TC-ANA-001` | Unit / Service | Admin analytics dashboard aggregation | Total revenue, tickets, bookings, occupancy computed correctly | **PASS** |
| **ANALYTICS**| `TC-ANA-002` | Unit / Service | Analytics caching (Cache MISS -> Cache HIT) | First call fetches DAO, second call returns cached dict within TTL | **PASS** |
| **ERRORS** | `TC-ERR-001` | Integration | Marshmallow schema validation error | Formatted 422 / 400 error payload returned | **PASS** |
| **ERRORS** | `TC-ERR-002` | Integration | Resource not found (`/events/999999`) | Handled with clean 404 response | **PASS** |
| **QA-E2E** | `TC-E2E-001` | Integration | Complete 27-step project lifecycle test (`test_final_project_qa.py`) | All 27 real-world workflow checkpoints verified | **PASS** |

---

## Detailed Test Case Specifications

### TC-AUTH-001: Customer Registration & Password Hashing
- **Preconditions**: User does not exist in database.
- **Steps**:
  1. POST `/api/auth/register` with `{ "name": "Jane Doe", "email": "jane@example.com", "password": "Password@123" }`.
- **Expected Outcome**: HTTP 201 Created, `password_hash` stored in database using strong hashing (PBKDF2/scrypt), plaintext password never persisted.
- **Status**: **PASS**

### TC-AUTH-003: JWT Authentication & Role Issuance
- **Preconditions**: Customer registered in database.
- **Steps**:
  1. POST `/api/auth/login` with email and password.
- **Expected Outcome**: HTTP 200 OK, response contains `access_token`, `refresh_token`, and user profile with `role="customer"`.
- **Status**: **PASS**

### TC-RBAC-001: Role-Based Access Control on Admin Endpoints
- **Preconditions**: Authenticated user with role `customer`.
- **Steps**:
  1. GET `/api/admin/events` with customer Bearer token.
- **Expected Outcome**: HTTP 403 Forbidden with error message `"Admin privilege required"`.
- **Status**: **PASS**

### TC-CSRF-001 & TC-CSRF-003: Hybrid Web CSRF & API Exemption
- **Preconditions**: Flask application running with Flask-WTF CSRFProtect.
- **Steps**:
  1. POST `/events/1/checkout` without CSRF token from web browser session -> HTTP 400 Bad Request.
  2. POST `/api/bookings` with `Authorization: Bearer <token>` and JSON body -> HTTP 201 Created (API exempt from form CSRF).
- **Status**: **PASS**

### TC-SET-002 & TC-SET-003: 1-Minute Concurrency Seat Hold & Conflict Prevention
- **Preconditions**: Event with configured seats.
- **Steps**:
  1. Customer A calls `POST /api/events/<id>/seats/<seat_id>/hold`.
  2. Seat status updates to `held`, `held_until` set to `utcnow() + 60s`.
  3. Customer B attempts `POST /api/events/<id>/seats/<seat_id>/hold` for the same seat.
- **Expected Outcome**: Customer A receives HTTP 201. Customer B receives HTTP 409 Conflict (`"Seat is currently held by another user"`).
- **Status**: **PASS**

### TC-PRM-001 to TC-PRM-005: Promo Code Engine
- **Preconditions**: Active promo codes (`WELCOME10`, `SAVE200`), expired code (`EXPIRED50`), and inactive code (`INACTIVE20`).
- **Steps**:
  1. Apply `WELCOME10` on ₹1,000 order -> Discount = ₹100.00, Final = ₹900.00.
  2. Apply `SAVE200` on ₹1,500 order -> Discount = ₹200.00, Final = ₹1,300.00.
  3. Apply `SAVE200` on ₹600 order -> Rejected ("Minimum booking amount of ₹1000.00 required").
  4. Apply `EXPIRED50` -> Rejected ("Promo code has expired").
  5. Apply `INACTIVE20` -> Rejected ("Invalid or inactive promo code").
- **Status**: **PASS**

### TC-RWD-001: 2% Cashback Wallet Credit
- **Preconditions**: User with `reward_balance = 0.00`.
- **Steps**:
  1. Confirm booking with final amount of ₹1,000.00.
- **Expected Outcome**: Exactly ₹20.00 (2%) credited to user's wallet, `RewardTransaction` recorded with `transaction_type="earned"`.
- **Status**: **PASS**

### TC-TCK-002 & TC-TCK-003: Door Scanner Verification & Double Scan Rejection
- **Preconditions**: Confirmed booking with issued digital ticket pass.
- **Steps**:
  1. Gate staff accesses `POST /api/tickets/verify/<ticket_token>` or `/verify/<ticket_token>`.
  2. Ticket status is updated to `used`, `verified_at` timestamp recorded.
  3. Gate staff scans the same ticket token a second time.
- **Expected Outcome**: First scan returns HTTP 200 (`"Ticket verified successfully. Entry approved."`). Second scan returns HTTP 409 Conflict (`"Ticket has already been used and verified"`).
- **Status**: **PASS**

### TC-ANA-002: Analytics Performance TTL Caching
- **Preconditions**: Admin analytics service with 60-second in-memory cache.
- **Steps**:
  1. Call `get_dashboard_analytics()` -> Cache MISS (DAO queried, cache populated).
  2. Call `get_dashboard_analytics()` immediately -> Cache HIT (Returned from cache in <1ms without DB queries).
- **Status**: **PASS**

---

## QA Execution Command Suite

```bash
# 1. Run all unit and service tests
uv run pytest -m unit

# 2. Run all model and relationship tests
uv run pytest -m model

# 3. Run all controller and blueprint tests
uv run pytest -m controller

# 4. Run all integration and security tests
uv run pytest -m integration

# 5. Run full test suite with test coverage
uv run pytest --cov

# 6. Run demo data seeding script
uv run python scripts/seed_demo_data.py
```
