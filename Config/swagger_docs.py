# Config/swagger_docs.py
#
# Complete OpenAPI 2.0 / Swagger Specification for SeatMeUp Event Ticket Booking REST API.
#
# Provides interactive documentation at /apidocs/ with JWT Bearer authorization,
# reusable schema definitions, and complete endpoints across all application modules.

from flasgger import Swagger

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "title": "SeatMeUp Event Ticket Booking API",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "SeatMeUp Event Ticket Booking API",
        "description": (
            "Interactive REST API documentation for SeatMeUp — Smart Event Ticket Booking & "
            "Seat Selection Platform.\n\n"
            "### Core Business Workflows:\n"
            "1. **Authentication**: Register customer account → Login → Receive JWT Bearer token.\n"
            "2. **Event Browsing**: Browse categories → Filter events → View venue seat maps.\n"
            "3. **Seat Hold & Concurrency**: Place a real-time 1-minute hold on desired seats → "
            "prevents other buyers from acquiring the same seats.\n"
            "4. **Checkout & 2% Cashback**: Confirm booking → Consume hold → Credit 2% cashback reward "
            "to user account ledger → Issue ticket with unique QR token.\n"
            "5. **Gate Admission & Anti-Double Scan**: Scan QR ticket at entrance → First scan admits "
            "and marks ticket as `used` → Subsequent scans are blocked with 409 Conflict.\n"
            "6. **Rescheduling & Audit**: Admin reschedules event with password verification → Logs "
            "audit trail → Dispatches notifications and emails to all ticket holders.\n"
            "7. **Admin Analytics**: Query revenue, occupancy, category breakdowns, and ticket metrics."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "SeatMeUp Engineering Team",
            "email": "support@seatmeup.com",
        },
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using Bearer scheme. Enter: `Bearer <your_token>`",
        }
    },
    "tags": [
        {"name": "Authentication", "description": "Customer registration, login, JWT token issuance, and profile retrieval."},
        {"name": "Users", "description": "User profile management and administrative user CRUD operations."},
        {"name": "Categories", "description": "Event genre and category classification catalog."},
        {"name": "Venues", "description": "Venue management, capacity configuration, and physical layout setup."},
        {"name": "Events", "description": "Event catalog, scheduling, pricing, search, and lifecycle management."},
        {"name": "Seats", "description": "Venue seating configurations and dynamic event seat map availability."},
        {"name": "Seat Holds", "description": "1-minute temporary seat hold concurrency barrier and hold lifecycle."},
        {"name": "Bookings", "description": "Checkout preview, atomic booking confirmation, 2% cashback rewards, and cancellations."},
        {"name": "Promo Codes", "description": "Promotional discount codes, percentage/fixed savings, and validation."},
        {"name": "Tickets", "description": "Digital ticket retrieval, PDF ticket download, and QR code token data."},
        {"name": "Ticket Verification", "description": "Venue door QR scanning, admission validation, and anti-double scan protection."},
        {"name": "Notifications", "description": "Customer in-app notification alerts for bookings, cancellations, and reschedules."},
        {"name": "Event Rescheduling", "description": "Administrative event rescheduling with password confirmation and audit logging."},
        {"name": "Admin Analytics", "description": "Executive dashboard metrics, gross revenue, occupancy, and sales breakdown."},
    ],
    "definitions": {
        "StandardSuccess": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "message": {"type": "string", "example": "Operation completed successfully"},
                "data": {"type": "object"},
            },
        },
        "StandardError": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "message": {"type": "string", "example": "Invalid request parameters or access denied"},
            },
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Alice Smith"},
                "email": {"type": "string", "example": "alice@seatmeup.com"},
                "role": {"type": "string", "enum": ["customer", "admin"], "example": "customer"},
                "phone": {"type": "string", "example": "+1-555-0199"},
                "id_document": {"type": "string", "example": "PASSPORT-A1234567"},
                "reward_balance": {"type": "number", "format": "float", "example": 25.50},
                "is_active": {"type": "boolean", "example": True},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
                "updated_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
            },
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Music"},
                "description": {"type": "string", "example": "Live concerts, festivals, and acoustic performances"},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
            },
        },
        "Venue": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "SeatMeUp Arena"},
                "address": {"type": "string", "example": "123 Stadium Road"},
                "city": {"type": "string", "example": "Goa"},
                "state": {"type": "string", "example": "GA"},
                "capacity": {"type": "integer", "example": 5000},
                "venue_type": {"type": "string", "enum": ["seated", "general"], "example": "seated"},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
                "updated_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
            },
        },
        "Event": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "category_id": {"type": "integer", "example": 1},
                "category_name": {"type": "string", "example": "Music"},
                "venue_id": {"type": "integer", "example": 1},
                "venue_name": {"type": "string", "example": "SeatMeUp Arena"},
                "venue_city": {"type": "string", "example": "Goa"},
                "created_by": {"type": "integer", "example": 1},
                "title": {"type": "string", "example": "Goa Music Nights 2026"},
                "description": {"type": "string", "example": "Epic beachside live music festival featuring international artists."},
                "event_date": {"type": "string", "format": "date", "example": "2026-09-15"},
                "start_time": {"type": "string", "example": "19:00:00"},
                "end_time": {"type": "string", "example": "23:00:00"},
                "poster": {"type": "string", "example": "uploads/goa_music.jpg"},
                "booking_open": {"type": "boolean", "example": True},
                "status": {"type": "string", "enum": ["draft", "published", "cancelled", "completed"], "example": "published"},
                "requires_seats": {"type": "boolean", "example": True},
                "base_price": {"type": "number", "format": "float", "example": 500.00},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
                "updated_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
            },
        },
        "Seat": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 10},
                "venue_id": {"type": "integer", "example": 1},
                "seat_number": {"type": "string", "example": "A-12"},
                "section_name": {"type": "string", "example": "VIP Orchestra"},
                "seat_type": {"type": "string", "example": "vip"},
                "price": {"type": "number", "format": "float", "example": 500.00},
                "is_active": {"type": "boolean", "example": True},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-01T10:00:00"},
            },
        },
        "SeatHold": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 101},
                "event_id": {"type": "integer", "example": 1},
                "seat_id": {"type": "integer", "example": 10},
                "user_id": {"type": "integer", "example": 2},
                "hold_token": {"type": "string", "example": "3b4f6e10-c12e-48a7-b248-8dfcb082e661"},
                "held_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:00:00"},
                "expires_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:01:00"},
                "status": {"type": "string", "enum": ["active", "expired", "consumed", "released"], "example": "active"},
            },
        },
        "Booking": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 50},
                "user_id": {"type": "integer", "example": 2},
                "event_id": {"type": "integer", "example": 1},
                "booking_reference": {"type": "string", "example": "SMU-C0E30B7D3513"},
                "total_amount": {"type": "number", "format": "float", "example": 980.00},
                "discount_amount": {"type": "number", "format": "float", "example": 200.00},
                "cashback_amount": {"type": "number", "format": "float", "example": 19.60},
                "status": {"type": "string", "enum": ["pending", "confirmed", "cancelled", "completed"], "example": "confirmed"},
                "booked_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:00:45"},
                "cancelled_at": {"type": "string", "format": "date-time", "example": None},
            },
        },
        "PromoCode": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "code": {"type": "string", "example": "SAVE20"},
                "description": {"type": "string", "example": "20% off bookings over ₹500"},
                "discount_type": {"type": "string", "enum": ["percentage", "fixed"], "example": "percentage"},
                "discount_value": {"type": "number", "format": "float", "example": 20.00},
                "minimum_booking_amount": {"type": "number", "format": "float", "example": 500.00},
                "max_uses": {"type": "integer", "example": 100},
                "used_count": {"type": "integer", "example": 12},
                "valid_from": {"type": "string", "format": "date-time", "example": "2026-08-01T00:00:00"},
                "valid_until": {"type": "string", "format": "date-time", "example": "2026-12-31T23:59:59"},
                "is_active": {"type": "boolean", "example": True},
            },
        },
        "Ticket": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 75},
                "booking_id": {"type": "integer", "example": 50},
                "ticket_token": {"type": "string", "example": "TKT-B3E0341B08C4"},
                "ticket_status": {"type": "string", "enum": ["valid", "used", "cancelled", "expired"], "example": "valid"},
                "qr_data": {"type": "string", "example": "SMU-TKT-B3E0341B08C4-CONFIRMED"},
                "issued_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:00:45"},
                "used_at": {"type": "string", "format": "date-time", "example": None},
                "expired_at": {"type": "string", "format": "date-time", "example": None},
            },
        },
        "TicketVerification": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 10},
                "ticket_id": {"type": "integer", "example": 75},
                "verification_status": {"type": "string", "enum": ["success", "failed"], "example": "success"},
                "verified_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:30:15"},
            },
        },
        "Notification": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 12},
                "user_id": {"type": "integer", "example": 2},
                "title": {"type": "string", "example": "Booking Confirmed"},
                "message": {"type": "string", "example": "Your booking SMU-C0E30B7D3513 is confirmed! 2% cashback credited."},
                "notification_type": {"type": "string", "example": "booking_confirmation"},
                "is_read": {"type": "boolean", "example": False},
                "created_at": {"type": "string", "format": "date-time", "example": "2026-08-23T20:00:46"},
            },
        },
        "EventReschedule": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 5},
                "event_id": {"type": "integer", "example": 1},
                "admin_id": {"type": "integer", "example": 1},
                "old_event_date": {"type": "string", "format": "date", "example": "2026-09-15"},
                "old_start_time": {"type": "string", "example": "19:00:00"},
                "new_event_date": {"type": "string", "format": "date", "example": "2026-09-22"},
                "new_start_time": {"type": "string", "example": "20:00:00"},
                "reason": {"type": "string", "example": "Artist schedule conflict"},
                "rescheduled_at": {"type": "string", "format": "date-time", "example": "2026-08-23T21:00:00"},
            },
        },
        "AnalyticsSummary": {
            "type": "object",
            "properties": {
                "total_events": {"type": "integer", "example": 15},
                "active_events": {"type": "integer", "example": 12},
                "total_bookings": {"type": "integer", "example": 180},
                "cancelled_bookings": {"type": "integer", "example": 8},
                "total_revenue": {"type": "number", "format": "float", "example": 85400.00},
                "cashback_given": {"type": "number", "format": "float", "example": 1708.00},
                "total_tickets_sold": {"type": "integer", "example": 320},
                "average_booking_value": {"type": "number", "format": "float", "example": 474.44},
            },
        },
    },
    "paths": {
        "/api/auth/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Register a new customer account",
                "description": "Creates a new customer account. Hashes password using PBKDF2/SHA256 and sets initial role to `customer`.",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "email", "password"],
                            "properties": {
                                "name": {"type": "string", "example": "Alice Smith"},
                                "email": {"type": "string", "example": "alice@seatmeup.com"},
                                "password": {"type": "string", "example": "SecurePass123!"},
                                "phone": {"type": "string", "example": "+1-555-0199"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Account created successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "User created"},
                                "data": {"$ref": "#/definitions/User"},
                            },
                        },
                    },
                    "400": {"description": "Missing required field (name, email, password)", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Email already registered", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Log in with email and password",
                "description": "Authenticates credentials and returns a signed JWT access token containing identity and role claims.",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["email", "password"],
                            "properties": {
                                "email": {"type": "string", "example": "alice@seatmeup.com"},
                                "password": {"type": "string", "example": "SecurePass123!"},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Authentication successful",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "Login successful"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "token": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
                                        "user": {"$ref": "#/definitions/User"},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Missing email or password", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Invalid email or password", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Account is inactive / banned", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get currently authenticated user profile",
                "description": "Extracts identity from active JWT and returns caller profile details without password hash.",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "User profile retrieved",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"$ref": "#/definitions/User"},
                            },
                        },
                    },
                    "401": {"description": "Authentication required or token expired", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/auth/customer-test": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Protected test endpoint for customers and admins",
                "description": "Verifies that caller possesses a valid customer or admin JWT token.",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Customer access granted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/auth/admin-test": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Protected test endpoint for admins only",
                "description": "Verifies that caller possesses an active admin JWT token.",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Admin access granted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Customer access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Log out API client",
                "description": "Clears JWT access cookies.",
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Logged out successfully", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Root alias for customer registration (/api/register)",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "email", "password"],
                            "properties": {
                                "name": {"type": "string", "example": "Alice Smith"},
                                "email": {"type": "string", "example": "alice@seatmeup.com"},
                                "password": {"type": "string", "example": "SecurePass123!"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Validation Error", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Root alias for user login (/api/login)",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["email", "password"],
                            "properties": {
                                "email": {"type": "string", "example": "alice@seatmeup.com"},
                                "password": {"type": "string", "example": "SecurePass123!"},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {"description": "Success", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Unauthorized", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/users": {
            "get": {
                "tags": ["Users"],
                "summary": "List all users (Admin only)",
                "description": "Returns complete list of all registered platform users.",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Users retrieved",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/User"}},
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "post": {
                "tags": ["Users"],
                "summary": "Create a user directly (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "email", "password_hash"],
                            "properties": {
                                "name": {"type": "string", "example": "Bob Jones"},
                                "email": {"type": "string", "example": "bob@example.com"},
                                "password_hash": {"type": "string", "example": "hashed_pass_string"},
                                "role": {"type": "string", "enum": ["customer", "admin"], "example": "customer"},
                                "phone": {"type": "string", "example": "+1-555-0144"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "User created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing required field", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Email already registered", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/users/{user_id}": {
            "get": {
                "tags": ["Users"],
                "summary": "Get user profile by ID (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "user_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User retrieved", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Users"],
                "summary": "Update user details (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "user_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "Alice Smith Updated"},
                                "phone": {"type": "string", "example": "+1-555-9999"},
                                "id_document": {"type": "string", "example": "DL-987654"},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Users"],
                "summary": "Delete a user (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "user_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/users/email/{email}": {
            "get": {
                "tags": ["Users"],
                "summary": "Get user by email (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "email", "in": "path", "type": "string", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User found", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "User not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/categories": {
            "get": {
                "tags": ["Categories"],
                "summary": "List all event categories (Public)",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Category catalog",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Category"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Categories"],
                "summary": "Create a new category (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "example": "Music"},
                                "description": {"type": "string", "example": "Live concerts and festivals"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Category created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing category name", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Category name already exists", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/categories/{category_id}": {
            "get": {
                "tags": ["Categories"],
                "summary": "Get category by ID (Public)",
                "parameters": [{"name": "category_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Category details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Category not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Categories"],
                "summary": "Update a category (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "category_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "Live Music"},
                                "description": {"type": "string", "example": "Updated description"},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Category updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Category not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Categories"],
                "summary": "Delete a category (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "category_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Category deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Category not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/venues": {
            "get": {
                "tags": ["Venues"],
                "summary": "List all venues (Public)",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Venue catalog",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Venue"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Venues"],
                "summary": "Create a new venue (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["name", "address"],
                            "properties": {
                                "name": {"type": "string", "example": "SeatMeUp Arena"},
                                "address": {"type": "string", "example": "123 Stadium Road"},
                                "city": {"type": "string", "example": "Goa"},
                                "state": {"type": "string", "example": "GA"},
                                "capacity": {"type": "integer", "example": 5000},
                                "venue_type": {"type": "string", "enum": ["seated", "general"], "example": "seated"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Venue created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing required fields or invalid capacity", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Venue name already exists in location", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/venues/{venue_id}": {
            "get": {
                "tags": ["Venues"],
                "summary": "Get venue details by ID (Public)",
                "parameters": [{"name": "venue_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Venue details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Venue not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Venues"],
                "summary": "Update venue details (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "venue_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "SeatMeUp Grand Arena"},
                                "capacity": {"type": "integer", "example": 5500},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Venue updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Venue not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Venues"],
                "summary": "Delete a venue (Admin only)",
                "description": "Deletes empty venue. Rejects deletion with 400 if active events are currently scheduled at this venue.",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "venue_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Venue deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Cannot delete venue with associated events", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Venue not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/events": {
            "get": {
                "tags": ["Events"],
                "summary": "List all events (Public)",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "List of events",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Event"}},
                            },
                        },
                    }
                },
            },
            "post": {
                "tags": ["Events"],
                "summary": "Create a new event (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["title", "category_id", "venue_id", "event_date", "start_time"],
                            "properties": {
                                "title": {"type": "string", "example": "Goa Music Nights 2026"},
                                "category_id": {"type": "integer", "example": 1},
                                "venue_id": {"type": "integer", "example": 1},
                                "event_date": {"type": "string", "format": "date", "example": "2026-09-15"},
                                "start_time": {"type": "string", "example": "19:00"},
                                "end_time": {"type": "string", "example": "23:00"},
                                "base_price": {"type": "number", "format": "float", "example": 500.00},
                                "requires_seats": {"type": "boolean", "example": True},
                                "booking_open": {"type": "boolean", "example": True},
                                "description": {"type": "string", "example": "Live music concert by the beach"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Event created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing required field or past date", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Category or Venue not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/events/upcoming": {
            "get": {
                "tags": ["Events"],
                "summary": "List all upcoming events (Public)",
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Upcoming events", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/events/category/{category_id}": {
            "get": {
                "tags": ["Events"],
                "summary": "List events by category (Public)",
                "parameters": [{"name": "category_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Events in category", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/events/search": {
            "get": {
                "tags": ["Events"],
                "summary": "Search events by title keyword (Public)",
                "parameters": [{"name": "q", "in": "query", "type": "string", "description": "Search keyword", "example": "Goa"}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Search results", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/events/{event_id}": {
            "get": {
                "tags": ["Events"],
                "summary": "Get event details by ID (Public)",
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Event details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Events"],
                "summary": "Update event details (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "event_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "example": "Goa Music Nights 2026 - Extended"},
                                "status": {"type": "string", "enum": ["draft", "published", "cancelled", "completed"], "example": "published"},
                                "base_price": {"type": "number", "format": "float", "example": 550.00},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Event updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Events"],
                "summary": "Delete an event (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Event deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/venues/{venue_id}/seats": {
            "get": {
                "tags": ["Seats"],
                "summary": "List all configured seats for a venue (Public)",
                "parameters": [{"name": "venue_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Venue seat layout",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Seat"}},
                            },
                        },
                    }
                },
            }
        },
        "/api/events/{event_id}/seats": {
            "get": {
                "tags": ["Seats"],
                "summary": "Get dynamic seat map with hold/booked states (Public / Optional JWT)",
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Seat map retrieved with status (available, held, held_by_me, booked)", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/events/{event_id}/seat-map": {
            "get": {
                "tags": ["Seats"],
                "summary": "Alias for seat map retrieval",
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Seat map retrieved", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/events/{event_id}/seats/{seat_id}/hold": {
            "post": {
                "tags": ["Seat Holds"],
                "summary": "Place a 1-minute hold on a seat",
                "description": "Creates a temporary 60-second hold locking the seat from concurrent buyers. Returns hold token and remaining seconds.",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "event_id", "in": "path", "type": "integer", "required": True},
                    {"name": "seat_id", "in": "path", "type": "integer", "required": True},
                ],
                "produces": ["application/json"],
                "responses": {
                    "201": {
                        "description": "Seat held successfully for 1 minute",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "Seat held successfully for 1 minute"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "hold_token": {"type": "string", "example": "3b4f6e10-c12e-48a7-b248-8dfcb082e661"},
                                        "seat_id": {"type": "integer", "example": 10},
                                        "event_id": {"type": "integer", "example": 1},
                                        "expires_at": {"type": "string", "example": "2026-08-23T20:01:00"},
                                        "remaining_seconds": {"type": "integer", "example": 60},
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Event or Seat not found for venue", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Seat already booked or held by another user", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/events/{event_id}/seats/{seat_id}/release": {
            "post": {
                "tags": ["Seat Holds"],
                "summary": "Release an active seat hold",
                "description": "Releases user's active seat hold back to available status.",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "event_id", "in": "path", "type": "integer", "required": True},
                    {"name": "seat_id", "in": "path", "type": "integer", "required": True},
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Seat hold released successfully", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Active hold not found for this user", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/seats/my-holds": {
            "get": {
                "tags": ["Seat Holds"],
                "summary": "List caller's active seat holds",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "event_id", "in": "query", "type": "integer", "required": False}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Active holds retrieved", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/checkout/preview": {
            "post": {
                "tags": ["Bookings"],
                "summary": "Preview checkout subtotal, promo savings, and 2% cashback",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["event_id"],
                            "properties": {
                                "event_id": {"type": "integer", "example": 1},
                                "promo_code": {"type": "string", "example": "SAVE20"},
                                "selected_addons": {"type": "object", "example": {"1": 2}},
                                "quantity": {"type": "integer", "example": 2},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Checkout preview breakdown",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "subtotal": {"type": "number", "example": 1000.00},
                                        "discount_amount": {"type": "number", "example": 200.00},
                                        "total_amount": {"type": "number", "example": 800.00},
                                        "cashback_amount": {"type": "number", "example": 16.00},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Missing event_id or invalid payload", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/checkout/confirm": {
            "post": {
                "tags": ["Bookings"],
                "summary": "Atomically confirm booking, issue ticket, and credit 2% cashback",
                "description": (
                    "Completes checkout in one atomic database transaction:\n"
                    "1. Consumes active seat holds (or reserves general admission tickets).\n"
                    "2. Calculates discount for valid promo code.\n"
                    "3. Credits exact 2% cashback to customer reward balance ledger.\n"
                    "4. Issues ticket with unique QR token and PDF receipt."
                ),
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["event_id"],
                            "properties": {
                                "event_id": {"type": "integer", "example": 1},
                                "promo_code": {"type": "string", "example": "SAVE20"},
                                "selected_addons": {"type": "object", "example": {"1": 1}},
                                "quantity": {"type": "integer", "example": 2},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Booking confirmed successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "Booking confirmed successfully!"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "booking_id": {"type": "integer", "example": 50},
                                        "booking_reference": {"type": "string", "example": "SMU-C0E30B7D3513"},
                                        "total_amount": {"type": "number", "example": 800.00},
                                        "discount_amount": {"type": "number", "example": 200.00},
                                        "cashback_amount": {"type": "number", "example": 16.00},
                                        "ticket_token": {"type": "string", "example": "TKT-B3E0341B08C4"},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Missing event_id or no active seat holds found", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/bookings": {
            "post": {
                "tags": ["Bookings"],
                "summary": "Alias for /api/checkout/confirm",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["event_id"],
                            "properties": {
                                "event_id": {"type": "integer", "example": 1},
                                "promo_code": {"type": "string", "example": "SAVE20"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Booking confirmed", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                },
            }
        },
        "/api/bookings/my": {
            "get": {
                "tags": ["Bookings"],
                "summary": "List all bookings for authenticated customer",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "User booking history",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Booking"}},
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/bookings/{booking_id}": {
            "get": {
                "tags": ["Bookings"],
                "summary": "Get booking details by ID (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "booking_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Booking retrieved", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Bookings"],
                "summary": "Update a booking (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "booking_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "enum": ["pending", "confirmed", "cancelled", "completed"], "example": "completed"},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Booking updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Bookings"],
                "summary": "Delete a booking (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "booking_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Booking deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/bookings/{booking_id}/cancel": {
            "post": {
                "tags": ["Bookings"],
                "summary": "Cancel booking, invalidate ticket, and reverse 2% cashback",
                "description": "Marks booking as cancelled, invalidates admission ticket, and reverses credited 2% cashback reward.",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "booking_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Booking cancelled and cashback reversed", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Booking already cancelled or past event", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/bookings/{booking_id}/send-confirmation": {
            "post": {
                "tags": ["Bookings"],
                "summary": "Resend booking confirmation email with PDF ticket (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "booking_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Confirmation email sent", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                    "500": {"description": "SMTP delivery failure", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/bookings/reference/{reference}": {
            "get": {
                "tags": ["Bookings"],
                "summary": "Get booking by booking reference string (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "reference", "in": "path", "type": "string", "required": True, "example": "SMU-C0E30B7D3513"}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Booking details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Booking not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/users/{user_id}/bookings": {
            "get": {
                "tags": ["Bookings"],
                "summary": "List bookings for a specific user (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "user_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User bookings", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/promos/validate": {
            "post": {
                "tags": ["Promo Codes"],
                "summary": "Validate promo code and calculate discount amount",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["code", "amount"],
                            "properties": {
                                "code": {"type": "string", "example": "SAVE20"},
                                "amount": {"type": "number", "format": "float", "example": 1000.00},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Promo valid",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "string", "example": "SAVE20"},
                                        "discount_type": {"type": "string", "example": "percentage"},
                                        "discount_value": {"type": "number", "example": 20.00},
                                        "discount_amount": {"type": "number", "example": 200.00},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Invalid promo code, expired, or minimum amount not met", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/promos": {
            "get": {
                "tags": ["Promo Codes"],
                "summary": "List all promo codes (Admin only)",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Promo codes list",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/PromoCode"}},
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "post": {
                "tags": ["Promo Codes"],
                "summary": "Create a new promo code (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["code", "discount_type", "discount_value"],
                            "properties": {
                                "code": {"type": "string", "example": "SAVE20"},
                                "description": {"type": "string", "example": "20% discount on orders over ₹500"},
                                "discount_type": {"type": "string", "enum": ["percentage", "fixed"], "example": "percentage"},
                                "discount_value": {"type": "number", "format": "float", "example": 20.00},
                                "minimum_booking_amount": {"type": "number", "format": "float", "example": 500.00},
                                "max_uses": {"type": "integer", "example": 100},
                                "valid_from": {"type": "string", "format": "date-time", "example": "2026-08-01T00:00:00"},
                                "valid_until": {"type": "string", "format": "date-time", "example": "2026-12-31T23:59:59"},
                                "is_active": {"type": "boolean", "example": True},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Promo code created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing required fields or invalid discount", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Promo code already exists", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/promos/{promo_id}": {
            "get": {
                "tags": ["Promo Codes"],
                "summary": "Get promo code details by ID (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "promo_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Promo code details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Promo code not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "put": {
                "tags": ["Promo Codes"],
                "summary": "Update a promo code (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "promo_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "discount_value": {"type": "number", "format": "float", "example": 25.00},
                                "is_active": {"type": "boolean", "example": True},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Promo code updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Promo code not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Promo Codes"],
                "summary": "Delete a promo code (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "promo_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Promo code deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Promo code not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
        "/api/tickets/{ticket_id}": {
            "get": {
                "tags": ["Tickets"],
                "summary": "Get rich ticket details by numeric ID (Public/Owner)",
                "parameters": [{"name": "ticket_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Ticket details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Ticket not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/tickets/{token}": {
            "get": {
                "tags": ["Tickets"],
                "summary": "Get rich ticket details by token string (Public)",
                "parameters": [{"name": "token", "in": "path", "type": "string", "required": True, "example": "TKT-B3E0341B08C4"}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Ticket details", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Ticket not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/bookings/{booking_id}/ticket": {
            "get": {
                "tags": ["Tickets"],
                "summary": "Get ticket issued for a booking (Public/Owner)",
                "parameters": [{"name": "booking_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Ticket for booking", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "404": {"description": "Ticket not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/tickets/{ticket_id}/verify": {
            "post": {
                "tags": ["Ticket Verification"],
                "summary": "Verify ticket by ID at gate (Admin/Staff)",
                "parameters": [
                    {"name": "ticket_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": False,
                        "schema": {"type": "object", "properties": {"mark_as_used": {"type": "boolean", "example": True}}},
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Ticket admitted successfully", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Ticket is cancelled", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Ticket not found", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Anti-double scan: Ticket already used", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/tickets/verify": {
            "post": {
                "tags": ["Ticket Verification"],
                "summary": "Verify ticket token at venue gate (Admin/Staff)",
                "description": (
                    "Validates physical entrance QR token:\n"
                    "1. Confirms ticket is in `valid` status.\n"
                    "2. Sets status to `used` and records `used_at` timestamp.\n"
                    "3. Anti-double scan protection: Rejects subsequent scan attempts with 409 Conflict.\n"
                    "4. Creates audit log entry in `ticket_verifications` table."
                ),
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["ticket_token"],
                            "properties": {
                                "ticket_token": {"type": "string", "example": "TKT-B3E0341B08C4"},
                                "mark_as_used": {"type": "boolean", "example": True},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Ticket verified and admission granted",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "Ticket is valid. Marked as used."},
                                "data": {"$ref": "#/definitions/Ticket"},
                            },
                        },
                    },
                    "400": {"description": "Missing ticket_token or ticket is cancelled", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Ticket token not found", "schema": {"$ref": "#/definitions/StandardError"}},
                    "409": {"description": "Anti-double scan: Ticket has already been used", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/tickets/{ticket_id}/verifications": {
            "get": {
                "tags": ["Ticket Verification"],
                "summary": "Get scan audit history for a ticket",
                "parameters": [{"name": "ticket_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Scan audit history",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/TicketVerification"}},
                            },
                        },
                    },
                    "404": {"description": "Ticket not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/notifications/my": {
            "get": {
                "tags": ["Notifications"],
                "summary": "Get caller's in-app notifications",
                "security": [{"Bearer": []}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Notifications list",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/Notification"}},
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/users/{user_id}/notifications": {
            "get": {
                "tags": ["Notifications"],
                "summary": "List notifications for a specific user (Owner or Admin)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "user_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "User notifications", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Access forbidden", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/notifications": {
            "post": {
                "tags": ["Notifications"],
                "summary": "Create an in-app notification (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["user_id", "title", "message", "notification_type"],
                            "properties": {
                                "user_id": {"type": "integer", "example": 2},
                                "title": {"type": "string", "example": "Event Rescheduled"},
                                "message": {"type": "string", "example": "Your event has been rescheduled to Sep 22, 2026."},
                                "notification_type": {"type": "string", "example": "event_rescheduled"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Notification created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "400": {"description": "Missing required field", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/notifications/{notification_id}/read": {
            "put": {
                "tags": ["Notifications"],
                "summary": "Mark notification as read",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "notification_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Marked as read", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Notification not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/admin/analytics": {
            "get": {
                "tags": ["Admin Analytics"],
                "summary": "Get platform analytics and revenue summary (Admin only)",
                "description": "Aggregates revenue, 2% cashback granted, bookings, cancellations, top selling events, category breakdown, and daily sales trends.",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "days", "in": "query", "type": "integer", "description": "Filter by last N days (e.g. 30)", "example": 30}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Analytics data retrieved",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "summary": {"$ref": "#/definitions/AnalyticsSummary"},
                                        "top_events": {"type": "array", "items": {"type": "object"}},
                                        "revenue_by_category": {"type": "array", "items": {"type": "object"}},
                                        "sales_over_time": {"type": "array", "items": {"type": "object"}},
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/admin/events/{event_id}/reschedule": {
            "post": {
                "tags": ["Event Rescheduling"],
                "summary": "Reschedule event with admin password confirmation (Admin only)",
                "description": (
                    "Administrative event rescheduling:\n"
                    "1. Confirms admin password for security verification.\n"
                    "2. Validates new event date is in the future.\n"
                    "3. Updates event date and time.\n"
                    "4. Creates audit log record in `event_reschedules` table.\n"
                    "5. Dispatches in-app notifications and email updates to all affected ticket holders."
                ),
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "event_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["new_event_date", "new_start_time", "password"],
                            "properties": {
                                "new_event_date": {"type": "string", "format": "date", "example": "2026-09-22"},
                                "new_start_time": {"type": "string", "example": "20:00"},
                                "new_end_time": {"type": "string", "example": "23:30"},
                                "reason": {"type": "string", "example": "Artist schedule conflict"},
                                "password": {"type": "string", "example": "AdminPass123!"},
                            },
                        },
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Event rescheduled successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "message": {"type": "string", "example": "Event rescheduled successfully"},
                                "data": {"$ref": "#/definitions/Event"},
                            },
                        },
                    },
                    "400": {"description": "Missing password or past date", "schema": {"$ref": "#/definitions/StandardError"}},
                    "401": {"description": "Incorrect admin password", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "404": {"description": "Event not found", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/admin/events/{event_id}/reschedule-history": {
            "get": {
                "tags": ["Event Rescheduling"],
                "summary": "Get reschedule audit history for an event (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Reschedule audit logs",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "array", "items": {"$ref": "#/definitions/EventReschedule"}},
                            },
                        },
                    },
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/admin/events": {
            "post": {
                "tags": ["Events"],
                "summary": "Admin create event via /api/admin/events (Admin only)",
                "security": [{"Bearer": []}],
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["title", "category_id", "venue_id", "event_date", "start_time"],
                            "properties": {
                                "title": {"type": "string", "example": "Admin Created Event"},
                                "category_id": {"type": "integer", "example": 1},
                                "venue_id": {"type": "integer", "example": 1},
                                "event_date": {"type": "string", "format": "date", "example": "2026-09-20"},
                                "start_time": {"type": "string", "example": "18:00"},
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {"description": "Event created", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            }
        },
        "/api/admin/events/{event_id}": {
            "put": {
                "tags": ["Events"],
                "summary": "Admin update event via /api/admin/events/{event_id} (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "event_id", "in": "path", "type": "integer", "required": True},
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"type": "object", "properties": {"title": {"type": "string"}}},
                    },
                ],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Event updated", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
            "delete": {
                "tags": ["Events"],
                "summary": "Admin delete event via /api/admin/events/{event_id} (Admin only)",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "event_id", "in": "path", "type": "integer", "required": True}],
                "produces": ["application/json"],
                "responses": {
                    "200": {"description": "Event deleted", "schema": {"$ref": "#/definitions/StandardSuccess"}},
                    "401": {"description": "Authentication required", "schema": {"$ref": "#/definitions/StandardError"}},
                    "403": {"description": "Admin access required", "schema": {"$ref": "#/definitions/StandardError"}},
                },
            },
        },
    },
}


def init_swagger(app):
    """Initialize Flasgger with SeatMeUp OpenAPI specification."""
    return Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)
