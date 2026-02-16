# Testing Guide

## Overview

This guide covers all aspects of testing in the Trade Store application, including unit tests, integration tests, and end-to-end tests for both backend and frontend.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [E2E Testing](#e2e-testing)
5. [Test Coverage](#test-coverage)
6. [CI/CD Testing](#cicd-testing)
7. [Best Practices](#best-practices)

## Testing Philosophy

### Test-Driven Development (TDD)

We follow TDD principles for critical features:

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green

### Testing Pyramid

```
        /\
       /  \
      / E2E \          Few, slow, expensive
     /______\
    /        \
   /Integration\       Some, medium speed
  /____________\
 /              \
/   Unit Tests   \     Many, fast, cheap
/__________________\
```

### Test Coverage Goals

- **Backend**: >70% coverage
- **Frontend**: >80% coverage
- **Critical Paths**: 100% coverage

## Backend Testing

### Setup

```bash
cd backend
poetry install
poetry run pytest
```

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py          # Fixtures and configuration
├── test_api.py          # API endpoint tests
├── test_services.py     # Service layer tests
└── test_repositories.py # Repository layer tests
```

### Fixtures

#### Database Fixture

```python
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

#### Test Client Fixture

```python
@pytest.fixture(scope="function")
def client(db_session: Session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

#### Sample Data Fixture

```python
@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing."""
    return {
        "trade_id": "T1",
        "version": 1,
        "counter_party_id": "CP-1",
        "book_id": "B1",
        "maturity_date": (date.today() + timedelta(days=30)).isoformat()
    }
```

### Unit Tests

#### Testing Services

```python
def test_create_trade_success(db_session: Session, sample_trade_data: dict):
    """Test successful trade creation."""
    service = TradeService(db_session)
    trade_create = TradeCreate(**sample_trade_data)
    
    trade = service.create_trade(trade_create)
    
    assert trade.trade_id == sample_trade_data["trade_id"]
    assert trade.version == sample_trade_data["version"]
    assert trade.id is not None


def test_create_trade_past_maturity_date(db_session: Session):
    """Test trade creation with past maturity date fails."""
    service = TradeService(db_session)
    trade_data = TradeCreate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() - timedelta(days=1)
    )
    
    with pytest.raises(MaturityDateException):
        service.create_trade(trade_data)


def test_version_conflict(db_session: Session, sample_trade_data: dict):
    """Test version conflict detection."""
    service = TradeService(db_session)
    
    # Create first trade
    trade_create = TradeCreate(**sample_trade_data)
    service.create_trade(trade_create)
    
    # Try to create with lower version
    trade_create.version = 0
    with pytest.raises(VersionConflictException):
        service.create_trade(trade_create)
```

#### Testing Repositories

```python
def test_repository_get_all(db_session: Session):
    """Test repository get_all method."""
    repository = TradeRepository(db_session)
    
    # Create test trades
    for i in range(5):
        trade = TradeDB(
            trade_id=f"T{i}",
            version=1,
            counter_party_id=f"CP-{i}",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30)
        )
        db_session.add(trade)
    db_session.commit()
    
    # Test pagination
    trades, total = repository.get_all(skip=0, limit=3)
    
    assert len(trades) == 3
    assert total == 5


def test_repository_filtering(db_session: Session):
    """Test repository filtering."""
    repository = TradeRepository(db_session)
    
    # Create trades with different book IDs
    for book_id in ["B1", "B2"]:
        trade = TradeDB(
            trade_id=f"T-{book_id}",
            version=1,
            counter_party_id="CP-1",
            book_id=book_id,
            maturity_date=date.today() + timedelta(days=30)
        )
        db_session.add(trade)
    db_session.commit()
    
    # Filter by book_id
    trades, total = repository.get_all(book_id="B1")
    
    assert total == 1
    assert trades[0].book_id == "B1"
```

### Integration Tests

#### Testing API Endpoints

```python
def test_create_trade_endpoint(client: TestClient, sample_trade_data: dict):
    """Test POST /api/v1/trades endpoint."""
    response = client.post("/api/v1/trades", json=sample_trade_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["trade_id"] == sample_trade_data["trade_id"]
    assert "id" in data


def test_get_trades_endpoint(client: TestClient, sample_trade_data: dict):
    """Test GET /api/v1/trades endpoint."""
    # Create a trade first
    client.post("/api/v1/trades", json=sample_trade_data)
    
    # Get trades
    response = client.get("/api/v1/trades?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "trades" in data
    assert "total" in data
    assert len(data["trades"]) > 0


def test_update_trade_endpoint(client: TestClient, sample_trade_data: dict):
    """Test PUT /api/v1/trades/{id} endpoint."""
    # Create trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]
    
    # Update trade
    updated_data = sample_trade_data.copy()
    updated_data["counter_party_id"] = "CP-2"
    response = client.put(f"/api/v1/trades/{trade_id}", json=updated_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["counter_party_id"] == "CP-2"


def test_delete_trade_endpoint(client: TestClient, sample_trade_data: dict):
    """Test DELETE /api/v1/trades/{id} endpoint."""
    # Create trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]
    
    # Delete trade
    response = client.delete(f"/api/v1/trades/{trade_id}")
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404
```

### Running Backend Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_api.py

# Run specific test
poetry run pytest tests/test_api.py::test_create_trade_endpoint

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run with coverage and show missing lines
poetry run pytest --cov=app --cov-report=term-missing

# Run tests matching pattern
poetry run pytest -k "test_create"

# Run tests with markers
poetry run pytest -m "slow"
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install
npm test
```

### Test Structure

```
frontend/src/tests/
├── setup.ts              # Test configuration
├── unit/                 # Unit tests
│   ├── TradeFormDialog.test.tsx
│   └── utils.test.ts
├── integration/          # Integration tests
│   └── TradesPage.test.tsx
└── e2e/                  # E2E tests
    └── trades.spec.ts
```

### Unit Tests

#### Testing Components

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TradeFormDialog from '@/components/TradeFormDialog';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('TradeFormDialog', () => {
  it('renders create form when no trade provided', () => {
    const onClose = vi.fn();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <TradeFormDialog
        open={true}
        trade={null}
        onClose={onClose}
        onSuccess={onSuccess}
        onError={onError}
      />,
      { wrapper }
    );

    expect(screen.getByText('Create Trade')).toBeInTheDocument();
    expect(screen.getByLabelText(/Trade ID/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <TradeFormDialog
        open={true}
        trade={null}
        onClose={onClose}
        onSuccess={onSuccess}
        onError={onError}
      />,
      { wrapper }
    );

    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Trade ID is required/i)).toBeInTheDocument();
    });
  });

  it('calls onSuccess when trade created', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onSuccess = vi.fn();
    const onError = vi.fn();

    render(
      <TradeFormDialog
        open={true}
        trade={null}
        onClose={onClose}
        onSuccess={onSuccess}
        onError={onError}
      />,
      { wrapper }
    );

    // Fill form
    await user.type(screen.getByLabelText(/Trade ID/i), 'T999');
    await user.type(screen.getByLabelText(/Version/i), '1');
    await user.type(screen.getByLabelText(/Counter Party ID/i), 'CP-999');
    await user.type(screen.getByLabelText(/Book ID/i), 'B999');
    
    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
```

#### Testing Utilities

```typescript
import { describe, it, expect } from 'vitest';
import { formatDate, isExpired } from '@/utils/dateUtils';

describe('dateUtils', () => {
  describe('formatDate', () => {
    it('formats ISO date to dd/MM/yyyy', () => {
      const result = formatDate('2024-02-10');
      expect(result).toBe('10/02/2024');
    });

    it('handles invalid dates gracefully', () => {
      const result = formatDate('invalid');
      expect(result).toBe('invalid');
    });
  });

  describe('isExpired', () => {
    it('returns true for past dates', () => {
      const pastDate = '2020-01-01';
      expect(isExpired(pastDate)).toBe(true);
    });

    it('returns false for future dates', () => {
      const futureDate = '2099-12-31';
      expect(isExpired(futureDate)).toBe(false);
    });
  });
});
```

### Integration Tests

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import TradesPage from '@/pages/TradesPage';

const queryClient = new QueryClient();

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>{children}</BrowserRouter>
  </QueryClientProvider>
);

describe('TradesPage Integration', () => {
  it('displays trades and allows creation', async () => {
    const user = userEvent.setup();
    
    render(<TradesPage />, { wrapper });

    // Wait for page to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /trades/i })).toBeInTheDocument();
    });

    // Click create button
    const createButton = screen.getByRole('button', { name: /create trade/i });
    await user.click(createButton);

    // Dialog should open
    expect(screen.getByText('Create Trade')).toBeInTheDocument();
  });
});
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- TradeFormDialog.test.tsx

# Run tests matching pattern
npm test -- --grep "validation"

# Update snapshots
npm test -- -u
```

## E2E Testing

### Setup

```bash
cd frontend
npx playwright install
npm run test:e2e
```

### E2E Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Trade Store E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display trades page', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /trades/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /create trade/i })).toBeVisible();
  });

  test('should create trade successfully', async ({ page }) => {
    // Click create button
    await page.getByRole('button', { name: /create trade/i }).click();
    
    // Fill form
    await page.getByLabel(/Trade ID/i).fill('T999');
    await page.getByLabel(/Version/i).fill('1');
    await page.getByLabel(/Counter Party ID/i).fill('CP-999');
    await page.getByLabel(/Book ID/i).fill('B999');
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    await page.getByLabel(/Maturity Date/i).fill(tomorrow.toISOString().split('T')[0]);
    
    // Submit
    await page.getByRole('button', { name: /^create$/i }).click();
    
    // Verify success
    await expect(page.getByText(/Trade created successfully/i)).toBeVisible();
  });

  test('should validate maturity date', async ({ page }) => {
    await page.getByRole('button', { name: /create trade/i }).click();
    
    // Fill form with past maturity date
    await page.getByLabel(/Trade ID/i).fill('T999');
    await page.getByLabel(/Version/i).fill('1');
    await page.getByLabel(/Counter Party ID/i).fill('CP-999');
    await page.getByLabel(/Book ID/i).fill('B999');
    await page.getByLabel(/Maturity Date/i).fill('2020-01-01');
    
    await page.getByRole('button', { name: /^create$/i }).click();
    
    // Should show validation error
    await expect(page.getByText(/maturity date cannot be in the past/i)).toBeVisible();
  });

  test('should edit trade', async ({ page }) => {
    // Assuming there's at least one trade
    await page.getByLabel(/edit trade/i).first().click();
    
    // Update counter party
    await page.getByLabel(/Counter Party ID/i).clear();
    await page.getByLabel(/Counter Party ID/i).fill('CP-UPDATED');
    
    await page.getByRole('button', { name: /update/i }).click();
    
    // Verify success
    await expect(page.getByText(/Trade updated successfully/i)).toBeVisible();
  });

  test('should delete trade', async ({ page }) => {
    // Click delete button
    await page.getByLabel(/delete trade/i).first().click();
    
    // Confirm deletion
    await page.getByRole('button', { name: /delete/i }).click();
    
    // Trade should be removed (no success message for delete)
  });

  test('should filter trades', async ({ page }) => {
    // Use quick filter
    await page.getByPlaceholder(/search/i).fill('T1');
    
    // Wait for filtered results
    await page.waitForTimeout(1000);
    
    // Verify filtered results
    const rows = page.getByRole('row');
    await expect(rows).toHaveCount(expect.any(Number));
  });

  test('should toggle theme', async ({ page }) => {
    const themeButton = page.getByLabel(/toggle theme/i);
    await themeButton.click();
    
    // Check if theme changed
    const body = page.locator('body');
    await expect(body).toHaveCSS('background-color', /rgb/);
  });

  test('should navigate to about page', async ({ page }) => {
    await page.getByRole('button', { name: /about/i }).click();
    await expect(page.getByRole('heading', { name: /about trade store/i })).toBeVisible();
  });
});
```

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run in headed mode
npm run test:e2e -- --headed

# Run with UI
npm run test:e2e:ui

# Run specific test
npm run test:e2e -- trades.spec.ts

# Run in specific browser
npm run test:e2e -- --project=chromium

# Debug mode
npm run test:e2e -- --debug
```

## Test Coverage

### Viewing Coverage Reports

#### Backend

```bash
cd backend
poetry run pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

#### Frontend

```bash
cd frontend
npm run test:coverage
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
```

### Coverage Thresholds

#### Backend (pytest.ini)

```ini
[tool:pytest]
addopts = --cov-fail-under=70
```

#### Frontend (vitest.config.ts)

```typescript
coverage: {
  statements: 80,
  branches: 80,
  functions: 80,
  lines: 80,
}
```

## CI/CD Testing

### GitHub Actions

Tests run automatically on:
- Push to main/develop
- Pull requests

#### Backend CI

```yaml
- name: Run tests with coverage
  run: poetry run pytest --cov=app --cov-report=xml

- name: Check coverage threshold
  run: poetry run pytest --cov=app --cov-fail-under=70
```

#### Frontend CI

```yaml
- name: Run unit tests
  run: npm run test:coverage

- name: Run E2E tests
  run: npm run test:e2e
```

## Best Practices

### General

1. **Test Behavior, Not Implementation**
   - Focus on what the code does, not how
   - Test from user's perspective

2. **Keep Tests Independent**
   - Each test should run in isolation
   - Use fixtures for setup/teardown

3. **Use Descriptive Names**
   ```python
   # Good
   def test_create_trade_with_past_maturity_date_fails():
   
   # Bad
   def test_trade_1():
   ```

4. **Follow AAA Pattern**
   - Arrange: Set up test data
   - Act: Execute the code
   - Assert: Verify results

5. **Don't Test Third-Party Code**
   - Trust that libraries work
   - Test your integration with them

### Backend

1. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def sample_trade():
       return TradeCreate(...)
   ```

2. **Mock External Dependencies**
   ```python
   @patch('app.services.external_api')
   def test_with_mock(mock_api):
       mock_api.return_value = {...}
   ```

3. **Test Edge Cases**
   - Empty inputs
   - Boundary values
   - Error conditions

### Frontend

1. **Query by Accessibility**
   ```typescript
   // Good
   screen.getByRole('button', { name: /create/i })
   
   // Avoid
   screen.getByTestId('create-button')
   ```

2. **Wait for Async Operations**
   ```typescript
   await waitFor(() => {
     expect(screen.getByText(/success/i)).toBeInTheDocument();
   });
   ```

3. **Test User Interactions**
   ```typescript
   const user = userEvent.setup();
   await user.click(button);
   await user.type(input, 'text');
   ```

### E2E

1. **Test Critical User Flows**
   - Happy paths
   - Common error scenarios
   - Key business rules

2. **Use Page Object Pattern**
   ```typescript
   class TradesPage {
     async createTrade(data) {
       await this.page.getByRole('button', { name: /create/i }).click();
       // ... fill form
     }
   }
   ```

3. **Handle Flaky Tests**
   - Use proper waits
   - Avoid hard-coded timeouts
   - Retry on failure (CI only)

## Troubleshooting

### Common Issues

#### Backend

**Issue**: Tests fail with database errors
```bash
# Solution: Reset test database
rm test_trades.db
poetry run pytest
```

**Issue**: Import errors
```bash
# Solution: Reinstall dependencies
poetry install
```

#### Frontend

**Issue**: Tests timeout
```typescript
// Solution: Increase timeout
test('slow test', async () => {
  // ...
}, 10000); // 10 second timeout
```

**Issue**: Can't find element
```typescript
// Solution: Wait for element
await waitFor(() => {
  expect(screen.getByText(/text/i)).toBeInTheDocument();
});
```

#### E2E

**Issue**: Browser not installed
```bash
# Solution: Install browsers
npx playwright install
```

**Issue**: Tests fail in CI but pass locally
```typescript
// Solution: Add explicit waits
await page.waitForLoadState('networkidle');
```

## Conclusion

Comprehensive testing ensures code quality and prevents regressions. Follow the patterns and practices outlined in this guide to maintain high test coverage and reliability.
