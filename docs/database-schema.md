# Database Schema Documentation

## Overview

The Trade Store application uses SQLite for development (PostgreSQL-ready for production) with a single table for storing trade records.

**Database File Location:** `src/db/trades.db`

**ORM:** SQLAlchemy 2.0+

**Database Model Location:** `src/app/repositories/database.py`

---

## Tables

### `trades` Table

The main table storing all trade records with version history.

#### Columns

| Column Name       | Type          | Nullable | Default              | Description                                    |
|-------------------|---------------|----------|----------------------|------------------------------------------------|
| `id`              | INTEGER       | No       | Auto-increment       | Primary key, auto-generated unique identifier  |
| `trade_id`        | VARCHAR(50)   | No       | -                    | Business trade identifier (not unique)         |
| `version`         | INTEGER       | No       | -                    | Trade version number (≥1)                      |
| `counter_party_id`| VARCHAR(50)   | No       | -                    | Counter party identifier                       |
| `book_id`         | VARCHAR(50)   | No       | -                    | Book identifier for grouping trades            |
| `maturity_date`   | DATE          | No       | -                    | Trade maturity date (must be ≥ today UTC)      |
| `created_date`    | DATE          | No       | Current UTC date     | Date when trade was created (UTC)              |
| `expired`         | BOOLEAN       | No       | False                | Whether trade has expired (auto-updated)       |

#### Constraints

- **Primary Key:** `id`
- **Business Key:** Combination of `trade_id` + `version` (not enforced at DB level, handled in application logic)
- **Check Constraints:** Enforced at application level via Pydantic validation

---

## Indexes

The application uses strategic indexing to optimize query performance for common operations.

### Single Column Indexes

| Index Name        | Column        | Purpose                                           |
|-------------------|---------------|---------------------------------------------------|
| `ix_trades_id`    | `id`          | Primary key index (automatic)                     |
| `ix_trades_trade_id` | `trade_id` | Fast lookup by trade identifier                   |
| `ix_trades_book_id` | `book_id`   | Filter trades by book                             |
| `ix_trades_expired` | `expired`   | Filter active vs expired trades                   |

### Composite Indexes

| Index Name              | Columns                    | Purpose                                                    |
|-------------------------|----------------------------|------------------------------------------------------------|
| `idx_trade_id_version`  | `trade_id`, `version`      | **Critical:** Version conflict checks, lookup by trade+version |
| `idx_maturity_expired`  | `maturity_date`, `expired` | **Important:** Auto-expiry updates, filter by maturity status |

---

## Index Usage Patterns

### 1. `idx_trade_id_version` (Composite)

**Used by:**
- `get_by_trade_id_and_version()` - Exact lookup
- `get_latest_version()` - Find highest version for a trade_id
- Version conflict validation during trade creation

**Query Example:**
```sql
SELECT * FROM trades 
WHERE trade_id = 'T1' AND version = 2;

SELECT * FROM trades 
WHERE trade_id = 'T1' 
ORDER BY version DESC 
LIMIT 1;
```

**Why Critical:**
This is the most frequently used query pattern for enforcing business rules around trade versioning.

---

### 2. `idx_maturity_expired` (Composite)

**Used by:**
- `update_expired_trades()` - Runs on every `GET /trades` request
- Filtering expired vs active trades

**Query Example:**
```sql
UPDATE trades 
SET expired = TRUE 
WHERE maturity_date < CURRENT_DATE 
  AND expired = FALSE;

SELECT * FROM trades 
WHERE maturity_date >= '2024-01-01' 
  AND expired = FALSE;
```

**Why Important:**
The auto-expiry update runs frequently and needs to be fast. This composite index allows efficient filtering on both conditions.

---

### 3. `ix_trades_book_id` (Single)

**Used by:**
- Filtering trades by book in list queries
- Reporting and analytics by book

**Query Example:**
```sql
SELECT * FROM trades 
WHERE book_id = 'B1';
```

---

### 4. `ix_trades_expired` (Single)

**Used by:**
- Filtering active vs expired trades
- Dashboard queries showing only active trades

**Query Example:**
```sql
SELECT * FROM trades 
WHERE expired = FALSE;
```

---

## Business Rules Enforced

### 1. Version Validation
- **Rule:** Trades with lower versions are rejected
- **Implementation:** Application-level check using `get_latest_version()`
- **Index Used:** `idx_trade_id_version`

### 2. Same Version Replacement
- **Rule:** Trades with same version replace existing record
- **Implementation:** Application logic in service layer
- **Index Used:** `idx_trade_id_version`

### 3. Maturity Date Validation
- **Rule:** Maturity date must not be in the past (UTC)
- **Implementation:** Pydantic validator + service layer check
- **Index Used:** None (validation only)

### 4. Auto-Expiry
- **Rule:** Trades are automatically marked expired when maturity date passes
- **Implementation:** `update_expired_trades()` runs before each list query
- **Index Used:** `idx_maturity_expired`

---

## Performance Considerations

### Query Optimization

1. **Version Lookups:** O(log n) with `idx_trade_id_version`
2. **Expiry Updates:** O(log n) with `idx_maturity_expired`
3. **Book Filtering:** O(log n) with `ix_trades_book_id`
4. **Pagination:** Uses `LIMIT` and `OFFSET` with appropriate indexes

### Index Maintenance

- **Write Performance:** Minimal impact (4 single + 2 composite indexes)
- **Storage Overhead:** ~20-30% of table size
- **Update Cost:** Indexes updated automatically on INSERT/UPDATE

### Scalability

For production with large datasets:
- Consider partitioning by `created_date` or `book_id`
- Add covering indexes if specific query patterns emerge
- Monitor slow query log and adjust indexes accordingly

---

## Database Initialization

### Create Tables

```python
from src.app.repositories.database import init_db

init_db()
```

### Seed Sample Data

```bash
python src/seed_data.py
```

### Reset Database

```bash
rm src/db/trades.db
python -c "from src.app.repositories.database import init_db; init_db()"
```

---

## Migration Strategy

For production deployments, consider using Alembic for schema migrations:

```bash
# Install Alembic
poetry add alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## Database Configuration

### SQLite (Development)

```env
DATABASE_URL=sqlite:///./src/db/trades.db
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/tradestore
```

The application code is database-agnostic thanks to SQLAlchemy ORM.

---

## Monitoring Queries

### Check Index Usage (SQLite)

```sql
EXPLAIN QUERY PLAN 
SELECT * FROM trades 
WHERE trade_id = 'T1' AND version = 2;
```

### View Table Info

```sql
PRAGMA table_info(trades);
```

### View Indexes

```sql
PRAGMA index_list(trades);
```

### Table Statistics

```sql
SELECT COUNT(*) as total_trades FROM trades;
SELECT COUNT(*) as expired_trades FROM trades WHERE expired = TRUE;
SELECT COUNT(DISTINCT trade_id) as unique_trades FROM trades;
```

---

## Backup and Recovery

### Backup SQLite Database

```bash
# Simple copy
cp src/db/trades.db src/db/trades.db.backup

# Using SQLite command
sqlite3 src/db/trades.db ".backup 'src/db/trades.db.backup'"
```

### Restore

```bash
cp src/db/trades.db.backup src/db/trades.db
```

---

## Security Considerations

1. **SQL Injection Prevention:** Using SQLAlchemy ORM (parameterized queries)
2. **Access Control:** Database credentials in environment variables
3. **Data Validation:** Pydantic models validate all inputs
4. **Audit Trail:** `created_date` tracks when trades were created

---

## Future Enhancements

Potential schema improvements for future versions:

1. **Audit Table:** Track all changes to trades
2. **User Table:** Track who created/modified trades
3. **Soft Deletes:** Add `deleted_at` column instead of hard deletes
4. **Partitioning:** Partition by date for large datasets
5. **Full-Text Search:** Add FTS index for trade search
6. **Materialized Views:** For complex reporting queries
