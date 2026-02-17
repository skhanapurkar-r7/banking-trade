# Trade Store REST API

A production-ready REST API for managing trades with comprehensive validation, soft delete support, testing, and CI/CD pipeline.

## 🏗️ Architecture

- **Backend**: Python FastAPI + SQLite (PostgreSQL-ready)
- **Testing**: Pytest with TDD approach (57 tests, >70% coverage)
- **CI/CD**: GitHub Actions with multi-environment deployment
- **Architecture**: 3-tier (API → Service → Repository)
- **Features**: Soft delete, connection pooling, automatic expiry, pagination

## 📁 Project Structure

```
trade-store/
├── src/                      # Source code
│   ├── app/                  # Application code
│   │   ├── api/v1/          # API endpoints (versioned)
│   │   ├── services/        # Business logic
│   │   ├── repositories/    # Data access layer
│   │   ├── models/          # Pydantic models
│   │   └── core/            # Config, logging, exceptions
│   ├── tests/               # Pytest tests
│   ├── db/                  # Database files
│   └── seed_data.py         # Sample data seeder
├── .env/                    # Environment files
│   ├── .env.dev
│   ├── .env.staging
│   └── .env.production
├── docs/                    # Documentation
├── scripts/                 # Setup scripts
├── .github/workflows/       # CI/CD pipeline
├── pyproject.toml           # Poetry dependencies
├── poetry.lock              # Locked dependencies
├── Dockerfile               # Docker configuration
└── docker-compose.yml       # Docker Compose setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Poetry (will be installed by setup script)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/skhanapurkar-r7/banking-trade.git
cd banking-trade
```

2. **Setup Backend**
```bash
chmod +x scripts/setup-venv.sh
./scripts/setup-venv.sh
```

### Running the Application

```bash
# Activate virtual environment first
source venv/bin/activate

# Run with auto-reload (development)
uvicorn src.app.main:app --reload --port 8000
```

Access the API at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 💻 Development Commands

### Running the Application

```bash
# Navigate to backend directory
cd backend

# Run with auto-reload (development)
poetry run uvicorn app.main:app --reload

# Run on specific port
poetry run uvicorn app.main:app --reload --port 8000

# Run with specific host
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run without reload (production-like)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing Commands

```bash
cd backend

# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run tests with coverage
poetry run pytest --cov=app

# Run tests with coverage report (HTML)
poetry run pytest --cov=app --cov-report=html

# Run tests with coverage report (terminal with missing lines)
poetry run pytest --cov=app --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_api.py

# Run specific test function
poetry run pytest tests/test_api.py::test_create_trade

# Run tests matching a pattern
poetry run pytest -k "test_create"

# Run tests and stop on first failure
poetry run pytest -x

# Run tests with output (print statements)
poetry run pytest -s

# Check coverage threshold
poetry run pytest --cov=app --cov-fail-under=70
```

### Code Formatting Commands

```bash
# Format code with Black
poetry run black src/app src/tests

# Check formatting without making changes
poetry run black --check src/app src/tests

# Format specific file
poetry run black src/app/main.py

# Sort imports with isort
poetry run isort src/app src/tests

# Check import sorting without making changes
poetry run isort --check-only src/app src/tests
```

### Linting Commands

```bash
# Run Flake8 linter
poetry run flake8 src/app src/tests

# Run Flake8 with specific max line length
poetry run flake8 src/app src/tests --max-line-length=100

# Run Flake8 on specific file
poetry run flake8 src/app/main.py

# Show statistics
poetry run flake8 src/app src/tests --statistics
```

### Combined Quality Checks

```bash
# Run all quality checks (format, sort, lint)
poetry run black src/app src/tests && \
poetry run isort src/app src/tests && \
poetry run flake8 src/app src/tests

# Run all checks and tests
poetry run black src/app src/tests && \
poetry run isort src/app src/tests && \
poetry run flake8 src/app src/tests && \
pytest --cov=src/app
```

### Database Commands

```bash
# Initialize database
python -c "from src.app.repositories.database import init_db; init_db()"

# Seed sample data
python src/seed_data.py

# Reset database (delete and recreate)
rm src/db/trades.db
python -c "from src.app.repositories.database import init_db; init_db()"
```

### Poetry Commands

```bash
# Install dependencies
poetry install

# Install without dev dependencies
poetry install --no-dev

# Update dependencies
poetry update

# Add new dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Show installed packages
poetry show

# Show outdated packages
poetry show --outdated

# Activate virtual environment
poetry shell

# Run command in virtual environment
poetry run python script.py
```

### Useful Development Commands

```bash
# Check Python version
python --version

# Check FastAPI version
python -c "import fastapi; print(fastapi.__version__)"

# Start Python REPL with app context
python

# View API routes
python -c "from src.app.main import app; print(app.routes)"

# Generate requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t trade-store-api:latest .

# Run the container
docker run -d -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./db/trades.db \
  -e LOG_LEVEL=INFO \
  --name trade-store-api \
  trade-store-api:latest

# Check logs
docker logs trade-store-api

# Stop container
docker stop trade-store-api

# Remove container
docker rm trade-store-api
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

## 🚀 CI/CD Pipeline

### Pipeline Overview

The project includes a comprehensive CI/CD pipeline with:
- ✅ Automated linting and testing
- ✅ Security vulnerability scanning
- ✅ Docker image building and pushing
- ✅ Multi-environment deployment (DEV, STAGING, PROD)
- ✅ Approval-based deployments

### Deployment Environments

1. **DEV** and **STAGING**: Manual approval required for feature branch and Auto-deploy on merge to `main`
2. **PRODUCTION**: Release-based with approval

### Triggering Deployments

**Feature Development:**
```bash
git checkout -b feature/new-feature
# Make changes
git push origin feature/new-feature
# Create PR → Lint & Test run automatically
```

**Deploy to DEV & STAGING:**
```bash
# Merge PR to main
# DEV deploys automatically
# STAGING requires approval in GitHub Actions
```

**Deploy to PRODUCTION:**
```bash
# Create release on GitHub
# Tag: v1.0.0
# Approve deployment in GitHub Actions
```

See [Deployment Guide](docs/deployment.md) for detailed instructions.

## 📚 Documentation

### Essential Documentation for Submission

**Core Documentation:**
1. **[README.md](README.md)** - This file (Quick start, features, commands)
2. **[API Specification](docs/api-spec.md)** - Complete API reference with examples
3. **[Architecture](docs/architecture.md)** - System design and 3-tier architecture

**Implementation Details:**
4. **[Database Schema](docs/database-schema.md)** - Database design with soft delete
5. **[Testing Guide](docs/testing-guide.md)** - Test coverage and TDD approach
6. **[Deployment Guide](docs/deployment-guide.md)** - Docker and cloud deployment
7. **[CI/CD Documentation](docs/cicd-quick-reference.md)** - Pipeline configuration

## 🔐 Environment Variables

Create `.env/.env`:
```
DATABASE_URL=sqlite:///./src/db/trades.db
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

## 📦 Key Features

- ✅ Trade CRUD operations with validation
- ✅ **Soft Delete Implementation** - Trades marked as deleted, not removed
- ✅ Version conflict detection
- ✅ Maturity date validation (UTC timezone)
- ✅ Auto-expiry marking (background scheduler)
- ✅ Pagination, sorting, filtering
- ✅ **Connection Pooling** - Optimized database connections
- ✅ Comprehensive test coverage (57 tests, >70%)
- ✅ CI/CD pipeline with security scanning
- ✅ 3-tier architecture
- ✅ API versioning (/api/v1/)
- ✅ Structured logging
- ✅ Type hints and docstrings
- ✅ Docker support with health checks

## 🎯 Business Rules

1. **Version Validation**: Trades with lower versions are rejected
2. **Same Version**: Replaces existing trade
3. **Maturity Date**: Must not be in the past (UTC)
4. **Auto-Expiry**: Trades are marked expired when maturity date passes (background job)
5. **Soft Delete**: Deleted trades are marked with `is_deleted=true`, not physically removed
6. **Query Filtering**: Soft-deleted trades are excluded from all queries automatically

**Database Schema:**
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    trade_id VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL,
    counter_party_id VARCHAR(50) NOT NULL,
    book_id VARCHAR(50) NOT NULL,
    maturity_date DATE NOT NULL,
    created_date DATE NOT NULL,
    expired BOOLEAN NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,  -- Soft delete flag
    ...
);
CREATE INDEX ix_trades_is_deleted ON trades (is_deleted);
```

## 🏛️ Architecture Highlights

### 3-Tier Architecture

**API Layer** (`app/api/v1/`)
- Route handlers
- Request/response validation
- Error handling
- API versioning

**Service Layer** (`app/services/`)
- Business logic
- Version validation
- Maturity date checks
- Trade operations

**Repository Layer** (`app/repositories/`)
- Database operations
- Query building
- Data access abstraction

## 🛠️ Technology Stack

- **Framework**: FastAPI (high performance, auto-docs)
- **Database**: SQLite (development), PostgreSQL-ready
- **ORM**: SQLAlchemy (type-safe, migration-ready)
- **Validation**: Pydantic (runtime type checking)
- **Testing**: Pytest (TDD approach)
- **Linting**: Black, isort, Flake8
- **Logging**: Python logging module
- **Dependency Management**: Poetry

## 📊 API Endpoints

### Trades

- `GET /api/v1/trades` - List trades (paginated, filtered, sorted)
  - Query params: `page`, `page_size`, `trade_id`, `book_id`, `expired`, `sort_by`, `sort_order`
  - Excludes soft-deleted trades automatically
- `GET /api/v1/trades/{id}` - Get single trade (404 if soft-deleted)
- `POST /api/v1/trades` - Create trade
- `PUT /api/v1/trades/{id}` - Update trade (partial updates supported)
- `DELETE /api/v1/trades/{id}` - Soft delete trade (marks as deleted)

### Health

- `GET /health` - Basic health check
- `GET /health/db` - Database health with connection pool status

### Interactive Documentation

- `GET /docs` - Swagger UI (interactive API documentation)
- `GET /redoc` - ReDoc (alternative API documentation)

## 🧪 Test Coverage

- **Total Tests**: 57 tests
- **Coverage**: >70% (statements, branches, functions, lines)
- **Test Types**:
  - Unit tests for services and repositories
  - Integration tests for API endpoints
  - Business rule validation tests
  - Error handling tests
  - Soft delete functionality tests
  - Connection pooling tests
  - Scheduler tests

**Run Tests:**
```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src/app --cov-report=term-missing

# Run specific test file
poetry run pytest src/tests/test_api.py -v
```

## 🔄 CI/CD Pipeline

GitHub Actions workflow includes:
1. Install dependencies (Poetry)
2. Code formatting check (Black)
3. Import sorting check (isort)
4. Linting (Flake8)
5. Run tests with coverage
6. Coverage threshold check
7. Security vulnerability scan

Pipeline fails on:
- Linting errors
- Test failures
- Coverage below threshold
- Critical vulnerabilities

## 🔒 Security

- Input validation with Pydantic
- SQL injection prevention (ORM)
- CORS configuration
- Error message sanitization
- Environment variable usage
- Dependency vulnerability scanning

## 📈 Performance

- Database indexing on frequently queried fields (trade_id, book_id, expired, is_deleted)
- Pagination for large datasets
- Connection pooling (configurable for SQLite/PostgreSQL)
- Efficient query building with SQLAlchemy
- Background scheduler for automatic expiry updates

## 🚀 Deployment

See [Deployment Guide](docs/deployment-guide.md) for:
- Traditional server deployment
- Docker deployment
- Cloud platform deployment (AWS, Heroku, GCP)
- Database migration
- Monitoring setup

## 🤝 Contributing

1. Follow the existing code style
2. Write tests for new features (TDD)
3. Ensure all tests pass
4. Run linters before committing
5. Update documentation

## 📄 License

MIT

## 👥 Author

Trade Store Development Team
