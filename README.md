# RentACar API

## Implemented Features

### Authentication (`/api/auth/`)
-  User registration with validation
-  Login/Logout
-  Custom tokens (access + refresh)
-  Password change
-  Password recovery via token
-  Login history tracking
-  Device and IP tracking
-  Custom authentication middleware

### Accounts (`/api/accounts/`)
-  User profile management
-  Custom validations (email, username, password)
-  Complete REST serializers
-  Service layer

### Rentals (`/api/rentals/`)
-  Create/manage car rentals
-  Vehicle availability verification
-  Automatic price calculation
-  Date and period validation
-  Rental status (pending, confirmed, active, completed, cancelled, delayed)
-  Additional services (insurance, GPS, child seat, etc)

## Installation

### Windows PowerShell

```powershell
# 1. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables (create .env file)
# SECRET_KEY=your-secret-key-here
# DEBUG=True

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver 127.0.0.1:8000

# After starting, access: http://127.0.0.1:8000/api/
```

## API Documentation (Swagger/OpenAPI)

After starting the server, access the interactive documentation:

 URL | Description 
| **http://127.0.0.1:8000/api/docs/** |  **Swagger UI** - Interactive interface to test endpoints |
| **http://127.0.0.1:8000/api/redoc/** | **ReDoc** - Formatted and easy-to-read documentation |
| **http://127.0.0.1:8000/api/schema/** | **OpenAPI Schema** - API JSON schema (machine-readable) |

**Tips:**
- In Swagger UI, you can authenticate with JWT token and test all endpoints
- Documentation is auto-generated from code (Django REST Framework + drf-spectacular)
- All models, validations and types are documented

## Useful Commands

```bash
# Clean up expired tokens
python manage.py cleanup_tokens

# Clean up expired tokens (dry run)
python manage.py cleanup_tokens --dry-run

# Run tests
python manage.py test

# Run tests for a specific app
python manage.py test auth

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Monitoring (Prometheus/Grafana)

This service exposes application metrics for Prometheus at:

- Endpoint: `http://127.0.0.1:8000/metrics`

Quick setup:

1. Ensure the server is running and `/metrics` responds.
2. In Prometheus `prometheus.yml`, add a scrape job:

```yaml
scrape_configs:
  - job_name: 'rentacar'
    metrics_path: /metrics
    static_configs:
      - targets: ['127.0.0.1:8000']
```

3. In Grafana, add a Prometheus data source pointing to your Prometheus (e.g., `http://localhost:9090`).
4. Create dashboards using metrics like `http_requests_total`, `http_request_duration_seconds`, `rentals_created_total`.

See detailed instructions in `PROMETHEUS_GRAFANA.md`.

## Architecture

The project follows a layered architecture inspired by Alexandria API:

1. **Views** - API endpoints (REST)
2. **Serializers** - Data validation and serialization
3. **Services** - Separated business logic
4. **Models** - Data layer
5. **Validations** - Custom validations
6. **Types** - Type definitions (TypedDict)
7. **Docs** - Documentation per app

## Authentication

### Main Endpoints

```bash
POST /api/auth/register/      # Register user
POST /api/auth/login/         # Login
POST /api/auth/logout/        # Logout
POST /api/auth/token/refresh/ # Refresh token
POST /api/auth/password/change/        # Change password
POST /api/auth/password/reset/         # Request reset
POST /api/auth/password/reset/confirm/ # Confirm reset
GET  /api/auth/history/       # Login history
```

### Usage Example

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "confirm_password": "SecurePassword123"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "SecurePassword123"
  }'

# Response:
# {
#   "token": "abc123...",
#   "refresh_token": "xyz789...",
#   "expires_at": "2025-12-10T10:00:00Z"
# }

# 3. Use token in requests
curl -X GET http://localhost:8000/api/auth/history/ \
  -H "Authorization: Bearer abc123..."
```

## Tests

The project has **55 tests** with 100% coverage of main modules:

### Run Tests

```bash
# Run ALL tests
python manage.py test

# Run tests for a specific app
python manage.py test authentication   # Authentication tests
python manage.py test accounts        # Accounts tests
python manage.py test cars            # Cars tests
python manage.py test rentals         # Rentals tests

# Run with verbosity (shows each test)
python manage.py test --verbosity=2

# Run a specific test
python manage.py test authentication.tests.AuthenticationTests.test_user_registration

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML report in htmlcov/
```

### Test Coverage

- **Authentication (12 tests)**: Login, logout, tokens, refresh, history
- **Cars (12 tests)**: CRUD operations, brands, models, documents
- **Rentals (16 tests)**: Creation, cancellation, price calculation, availability
- **Services (16 tests)**: Business logic, validations, calculations
- **Models**: Referential integrity validations

### Expected Result

```
Found 55 test(s).
...................................................................
Ran 55 tests in ~25s
OK ✅
```

## Project Status 

-  Complete architecture 
-  Authentication with custom tokens
-  4 functional apps (authentication, accounts, cars, rentals)
-  9 database models
-  Service layer with business logic
-  55 tests passing (100% success)
-  Custom admin interface
-  Complete documentation

## Usage Examples

### 1. Register and Login

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "email": "maria@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "first_name": "Maria",
    "last_name": "Silva"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "token": "abc123xyz789...",
#   "refresh_token": "xyz789abc123...",
#   "expires_at": "2025-12-12T10:00:00Z",
#   "user": {...}
# }
```

### 2. List Cars

```bash
# With authentication
curl -X GET http://localhost:8000/api/cars/ \
  -H "Authorization: Bearer abc123xyz789..."

# Without authentication (public list)
curl -X GET http://localhost:8000/api/cars/
```

### 3. Create Rental

```bash
curl -X POST http://localhost:8000/api/rentals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer abc123xyz789..." \
  -d '{
    "car": 1,
    "start_date": "2025-12-15",
    "end_date": "2025-12-20",
    "driver_license": "12345678900",
    "with_insurance": true,
    "additional_services": [
      {"service": "gps", "quantity": 1},
      {"service": "child_seat", "quantity": 1}
    ]
  }'
```

### 4. Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "xyz789abc123..."
  }'
```

## Next Steps (Optional)

- [ ] Frontend in React/Vue
- [ ] Payment integration (Stripe/PayPal)
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)

## 🔌 Complete API Endpoints

### Interactive Documentation

```
GET  /api/schema/             - OpenAPI Schema (JSON)
GET  /api/docs/               - Swagger UI (interactive)
GET  /api/redoc/              - ReDoc (documentation)
```

### Authentication (`/api/auth/`)

```
POST /api/auth/register/              - Register new user
POST /api/auth/login/                 - Login
POST /api/auth/logout/                - Logout
POST /api/auth/token/refresh/         - Refresh access token
POST /api/auth/password/change/       - Change password
POST /api/auth/password/reset/        - Request password reset
POST /api/auth/password/reset/confirm/- Confirm reset with token
GET  /api/auth/history/               - List login history
GET  /api/auth/token/verify/          - Verify token
```

### Accounts (`/api/accounts/`)

```
GET  /api/accounts/                   - List all accounts (admin)
POST /api/accounts/                   - Create new account
GET  /api/accounts/{id}/              - Account details
PUT  /api/accounts/{id}/              - Update account (full)
PATCH /api/accounts/{id}/             - Update account (partial)
DELETE /api/accounts/{id}/            - Delete account
```

### Cars (`/api/cars/`)

```
GET  /api/cars/                       - List all cars
POST /api/cars/                       - Create new car (admin)
GET  /api/cars/{id}/                  - Car details
PUT  /api/cars/{id}/                  - Update car (admin)
PATCH /api/cars/{id}/                 - Update car partial (admin)
DELETE /api/cars/{id}/                - Delete car (admin)
GET  /api/cars/{id}/availability/    - Check availability
```

### Rentals (`/api/rentals/`)

```
GET  /api/rentals/                    - List rentals (own or all if admin)
POST /api/rentals/                    - Create new rental
GET  /api/rentals/{id}/               - Rental details
PUT  /api/rentals/{id}/               - Update rental
PATCH /api/rentals/{id}/              - Update rental (partial)
DELETE /api/rentals/{id}/             - Cancel rental
GET  /api/rentals/{id}/summary/       - Rental summary
POST /api/rentals/{id}/complete/      - Mark rental as complete
POST /api/rentals/{id}/cancel/        - Cancel with refund
```

### Admin

```
GET  /admin/                          - Django Admin
```

### Expected Status Codes

```
200 OK              - Success
201 Created         - Resource created
204 No Content      - Success without content
400 Bad Request     - Validation error
401 Unauthorized    - Not authenticated
403 Forbidden       - No permission
404 Not Found       - Resource not found
500 Server Error    - Server error
```
