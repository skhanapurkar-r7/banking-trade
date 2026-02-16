# Trade Store API Specification

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently no authentication required (development mode).

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response**
```json
{
  "status": "healthy"
}
```

---

### Trades

#### GET /api/v1/trades
Get paginated list of trades with filtering and sorting.

**Query Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number (1-indexed) |
| page_size | integer | No | 10 | Items per page (max 100) |
| trade_id | string | No | - | Filter by trade ID (partial match) |
| book_id | string | No | - | Filter by book ID (exact match) |
| expired | boolean | No | - | Filter by expired status |
| sort_by | string | No | id | Field to sort by |
| sort_order | string | No | asc | Sort order (asc/desc) |

**Response 200**
```json
{
  "trades": [
    {
      "id": 1,
      "trade_id": "T1",
      "version": 1,
      "counter_party_id": "CP-1",
      "book_id": "B1",
      "maturity_date": "2024-12-31",
      "created_date": "2024-02-10",
      "expired": false
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

---

#### GET /api/v1/trades/{id}
Get a single trade by database ID.

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Database ID of the trade |

**Response 200**
```json
{
  "id": 1,
  "trade_id": "T1",
  "version": 1,
  "counter_party_id": "CP-1",
  "book_id": "B1",
  "maturity_date": "2024-12-31",
  "created_date": "2024-02-10",
  "expired": false
}
```

**Response 404**
```json
{
  "detail": "Trade with ID 1 not found"
}
```

---

#### POST /api/v1/trades
Create a new trade.

**Request Body**
```json
{
  "trade_id": "T1",
  "version": 1,
  "counter_party_id": "CP-1",
  "book_id": "B1",
  "maturity_date": "2024-12-31"
}
```

**Validation Rules**
- `trade_id`: Required, 1-50 characters
- `version`: Required, integer >= 1
- `counter_party_id`: Required, 1-50 characters
- `book_id`: Required, 1-50 characters
- `maturity_date`: Required, must not be in the past

**Response 201**
```json
{
  "id": 1,
  "trade_id": "T1",
  "version": 1,
  "counter_party_id": "CP-1",
  "book_id": "B1",
  "maturity_date": "2024-12-31",
  "created_date": "2024-02-10",
  "expired": false
}
```

**Response 400 - Validation Error**
```json
{
  "detail": {
    "message": "Maturity date cannot be in the past",
    "details": {
      "maturity_date": "2020-01-01"
    }
  }
}
```

**Response 409 - Version Conflict**
```json
{
  "detail": {
    "message": "Trade version 1 is lower than existing version 2",
    "details": {
      "trade_id": "T1",
      "submitted_version": 1,
      "existing_version": 2
    }
  }
}
```

---

#### PUT /api/v1/trades/{id}
Update an existing trade.

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Database ID of the trade |

**Request Body**
```json
{
  "trade_id": "T1",
  "version": 2,
  "counter_party_id": "CP-2",
  "book_id": "B1",
  "maturity_date": "2024-12-31"
}
```

**Response 200**
```json
{
  "id": 1,
  "trade_id": "T1",
  "version": 2,
  "counter_party_id": "CP-2",
  "book_id": "B1",
  "maturity_date": "2024-12-31",
  "created_date": "2024-02-10",
  "expired": false
}
```

**Response 404**
```json
{
  "detail": "Trade with ID 1 not found"
}
```

**Response 400/409**
Same as POST endpoint

---

#### DELETE /api/v1/trades/{id}
Delete a trade.

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Database ID of the trade |

**Response 204**
No content

**Response 404**
```json
{
  "detail": "Trade with ID 1 not found"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message" | {
    "message": "Error message",
    "details": {}
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Validation error
- `404 Not Found`: Resource not found
- `409 Conflict`: Version conflict
- `500 Internal Server Error`: Server error

## Business Rules

### Version Validation
1. New trade version must be >= existing version for same trade_id
2. If version < existing: Return 409 error
3. If version = existing: Allow replacement (update)
4. If version > existing: Create new version

### Maturity Date Validation
1. Maturity date must not be in the past
2. Trades with past maturity dates are automatically marked as expired
3. Expired status is updated on each GET request

### Auto-Expiry
- System automatically marks trades as expired when maturity_date < today
- Happens during:
  - GET /trades (list)
  - Individual trade operations

## Rate Limiting
Currently no rate limiting (development mode).

## CORS
Configured to allow:
- Origins: `http://localhost:5173`, `http://localhost:3000`
- Methods: All
- Headers: All
- Credentials: Yes

## API Versioning
Current version: v1
- All endpoints prefixed with `/api/v1`
- Future versions will use `/api/v2`, etc.
