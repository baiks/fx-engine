# FX Engine - Foreign Exchange Trading System

A production-ready foreign exchange engine that handles currency conversions between USD, EUR, KES, and NGN with proper quote management, transaction execution, and exchange rate updates.

## Features

- **Quote Generation**: Generate FX quotes with configurable spreads and 60-second validity
- **Transaction Execution**: Execute quotes atomically with idempotency guarantees
- **Exchange Rate Management**: Update rates from external APIs or set manually
- **Decimal Precision**: All financial calculations use Python's Decimal type
- **Concurrent Request Handling**: Database-level locking prevents race conditions
- **Cross-Rate Calculation**: Automatic calculation of indirect currency pairs
- **Audit Trail**: Complete transaction history with timestamps

## Architecture

### Design Decisions

1. **Layered Architecture**
   - **Routes Layer**: HTTP endpoint handlers with validation
   - **Service Layer**: Business logic for FX operations and rate management
   - **Model Layer**: SQLAlchemy ORM models with proper relationships
   - **Utils Layer**: Reusable utilities for decimal math and validation

2. **Decimal Arithmetic**
   - All monetary values stored as `Numeric(18, 2)` in database
   - Python `Decimal` type used throughout to avoid floating-point errors
   - Explicit rounding with banker's rounding (ROUND_HALF_UP)

3. **Quote Validity & Expiration**
   - Quotes expire after 60 seconds (configurable)
   - Expiration checked at execution time
   - Prevents stale rate execution

4. **Concurrency Handling**
   - `SELECT ... FOR UPDATE` row-level locking on quote execution
   - Prevents double execution of same quote
   - Idempotent execution - returns existing transaction if already executed

5. **Spread Management**
   - Buy spread applied to all customer quotes
   - Configurable in basis points (50 bps = 0.5% by default)
   - Separate buy/sell spreads for flexibility

6. **Rate Discovery**
   - Direct rates stored in database
   - Inverse rates calculated automatically (if EUR/USD exists, calculate USD/EUR)
   - Cross rates calculated through USD (e.g., KES/NGN = KES/USD * USD/NGN)

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. **Create project structure**:
```bash
# Run the setup script
bash setup_commands.sh
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**:
```bash
# This will create tables and seed initial rates
flask seed-rates
```

### Running the Application

**Development mode**:
```bash
flask run
```

**Production mode**:
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app("production")'
```

The API will be available at `http://localhost:5000`

## API Documentation

## 🧪 API Testing with Postman

A ready-to-use Postman collection is included for quick testing.

👉 [Download Postman Collection](./api_collection.json)

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "FX Engine"
}
```

#### 2. Generate Quote
```http
POST /quotes
Content-Type: application/json

{
  "from_currency": "USD",
  "to_currency": "KES",
  "amount": "100.00"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "quote_id": "550e8400-e29b-41d4-a716-446655440000",
    "from_currency": "USD",
    "to_currency": "KES",
    "from_amount": "100.00",
    "to_amount": "13014.75",
    "exchange_rate": "130.1475",
    "created_at": "2024-11-12T10:30:00",
    "expires_at": "2024-11-12T10:31:00",
    "is_executed": false
  }
}
```

#### 3. Get Quote
```http
GET /quotes/{quote_id}
```

#### 4. Execute Transaction
```http
POST /transactions
Content-Type: application/json

{
  "quote_id": "550e8400-e29b-41d4-a716-446655440000",
  "idempotency_key": "optional-unique-key"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "transaction_id": "660e8400-e29b-41d4-a716-446655440000",
    "quote_id": "550e8400-e29b-41d4-a716-446655440000",
    "from_currency": "USD",
    "to_currency": "KES",
    "from_amount": "100.00",
    "to_amount": "13014.75",
    "exchange_rate": "130.1475",
    "status": "completed",
    "created_at": "2024-11-12T10:30:30"
  }
}
```

#### 5. Get Transaction
```http
GET /transactions/{transaction_id}
```

#### 6. Get Transaction History
```http
GET /transactions?limit=100
```

#### 7. Get All Exchange Rates
```http
GET /rates
```

#### 8. Update Rates from External API
```http
POST /rates/update
Content-Type: application/json

{
  "base_currency": "USD"
}
```

#### 9. Set Exchange Rate Manually
```http
POST /rates
Content-Type: application/json

{
  "base_currency": "USD",
  "target_currency": "KES",
  "rate": "129.50"
}
```

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_fx_service.py -v
```

### Test Coverage
- Core business logic (FX Service): ✅ Comprehensive
- Rate management: ✅ Comprehensive
- API endpoints: ✅ Comprehensive
- Decimal precision: ✅ Verified
- Concurrency: ✅ Tested
- Edge cases: ✅ Covered

## Supported Currency Pairs

### Direct Pairs
- USD/KES, USD/NGN, USD/EUR
- EUR/KES, EUR/NGN, EUR/USD

### Calculated Pairs
- KES/NGN, NGN/KES (via USD cross rate)
- All inverse pairs automatically available

## Technical Requirements Met

✅ **Correctness**: Decimal arithmetic for all financial calculations  
✅ **Design**: Layered architecture with clear separation of concerns  
✅ **Code Quality**: Clean, documented, type-hinted code  
✅ **Concurrency**: Row-level locking for atomic operations  
✅ **Error Handling**: Comprehensive validation and error responses  
✅ **Testing**: Full test coverage of business logic  
✅ **Documentation**: Complete API documentation and setup guide  

## Bonus Features Implemented

✅ **Idempotency**: Quote execution is idempotent - safe to retry  
✅ **Rate Staleness Detection**: Track rate update timestamps  
✅ **Transaction Audit Logging**: Complete history with relationships  
✅ **Cross-Rate Support**: Automatic calculation of indirect pairs  

## Known Limitations & Future Improvements

### Current Limitations

1. **No Authentication/Authorization**: Endpoints are public (intentional for demo)
2. **In-Memory Rate Updates**: External API calls are synchronous
3. **Simple Spread Model**: Fixed spreads, not dynamic based on liquidity
4. **No Rate Limits**: API endpoints have no rate limiting
5. **Single Database**: No read replicas or sharding

### With More Time, I Would Add

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - API key management

2. **Advanced Features**
   - Async rate updates with Celery
   - Redis caching for frequently accessed rates
   - WebSocket support for real-time rate streaming
   - Multi-currency wallet support
   - Batch transaction processing

3. **Observability**
   - Structured logging with correlation IDs
   - Prometheus metrics for monitoring
   - Distributed tracing with Jaeger
   - Custom dashboards for business metrics

4. **Reliability**
   - Circuit breakers for external API calls
   - Retry logic with exponential backoff
   - Dead letter queue for failed transactions
   - Database connection pooling optimization

5. **Compliance**
   - Regulatory reporting capabilities
   - KYC/AML integration hooks
   - Transaction limits and controls
   - Audit log encryption

6. **Performance**
   - Database query optimization
   - Read replicas for queries
   - Caching layer (Redis)
   - API response pagination

## Assumptions Made

1. **Quote Validity**: 60 seconds is sufficient for user interaction
2. **Spreads**: Same spread for all currency pairs (simplified model)
3. **Rate Updates**: Manual updates acceptable for demo (would use scheduled jobs in production)
4. **Base Currency**: USD is primary base for cross-rate calculations
5. **Transaction Finality**: All transactions are final once executed (no cancellations)
6. **Currency Precision**: 2 decimal places for amounts, 8 for rates
7. **Concurrency**: SQLite sufficient for demo (would use PostgreSQL in production)

## Project Structure

```
fx-engine/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── exchange_rate.py
│   │   ├── quote.py
│   │   └── transaction.py
│   ├── services/            # Business logic
│   │   ├── fx_service.py
│   │   └── rate_service.py
│   ├── routes/              # API endpoints
│   │   └── fx_routes.py
│   └── utils/               # Utilities
│       ├── decimal_utils.py
│       └── validators.py
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_fx_service.py
│   ├── test_rate_service.py
│   └── test_api.py
├── config.py               # Configuration
├── run.py                  # Application entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Time Spent

**Estimated Time**: ~6 hours

- Planning & Architecture: 1 hour
- Core Implementation: 3 hours
- Testing: 1.5 hours
- Documentation: 0.5 hours