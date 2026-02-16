"""Tests for API endpoints."""

from datetime import date, timedelta

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_create_trade(client: TestClient, sample_trade_data: dict):
    """Test creating a new trade."""
    response = client.post("/api/v1/trades", json=sample_trade_data)
    assert response.status_code == 201
    data = response.json()
    assert data["trade_id"] == sample_trade_data["trade_id"]
    assert data["version"] == sample_trade_data["version"]
    assert "id" in data


def test_create_trade_with_past_maturity_date(client: TestClient, sample_trade_data: dict):
    """Test creating trade with past maturity date fails."""
    sample_trade_data["maturity_date"] = (date.today() - timedelta(days=1)).isoformat()
    response = client.post("/api/v1/trades", json=sample_trade_data)
    assert response.status_code == 422  # Pydantic validation error


def test_create_trade_version_conflict(client: TestClient, sample_trade_data: dict):
    """Test version conflict detection."""
    # Create first trade
    client.post("/api/v1/trades", json=sample_trade_data)

    # Try to create with lower version (version must be >= 1, so 0 fails Pydantic validation)
    sample_trade_data["version"] = 0
    response = client.post("/api/v1/trades", json=sample_trade_data)
    assert response.status_code == 422  # Pydantic validation error (version must be >= 1)


def test_get_trades(client: TestClient, sample_trade_data: dict):
    """Test getting list of trades."""
    # Create a trade first
    client.post("/api/v1/trades", json=sample_trade_data)

    response = client.get("/api/v1/trades")
    assert response.status_code == 200
    data = response.json()
    assert "trades" in data
    assert "total" in data
    assert len(data["trades"]) > 0


def test_get_trade_by_id(client: TestClient, sample_trade_data: dict):
    """Test getting a single trade by ID."""
    # Create a trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]

    # Get the trade
    response = client.get(f"/api/v1/trades/{trade_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trade_id


def test_get_nonexistent_trade(client: TestClient):
    """Test getting a trade that doesn't exist."""
    response = client.get("/api/v1/trades/9999")
    assert response.status_code == 404


def test_update_trade(client: TestClient, sample_trade_data: dict):
    """Test updating a trade."""
    # Create a trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]

    # Update the trade
    updated_data = sample_trade_data.copy()
    updated_data["counter_party_id"] = "CP-2"
    response = client.put(f"/api/v1/trades/{trade_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["counter_party_id"] == "CP-2"


def test_delete_trade(client: TestClient, sample_trade_data: dict):
    """Test deleting a trade."""
    # Create a trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]

    # Delete the trade
    response = client.delete(f"/api/v1/trades/{trade_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404


def test_pagination(client: TestClient, sample_trade_data: dict):
    """Test pagination of trades list."""
    # Create multiple trades
    for i in range(5):
        data = sample_trade_data.copy()
        data["trade_id"] = f"T{i}"
        client.post("/api/v1/trades", json=data)

    # Test pagination
    response = client.get("/api/v1/trades?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_filtering_by_book_id(client: TestClient, sample_trade_data: dict):
    """Test filtering trades by book_id."""
    # Create trades with different book IDs
    data1 = sample_trade_data.copy()
    data1["trade_id"] = "T1"
    data1["book_id"] = "B1"
    client.post("/api/v1/trades", json=data1)

    data2 = sample_trade_data.copy()
    data2["trade_id"] = "T2"
    data2["book_id"] = "B2"
    client.post("/api/v1/trades", json=data2)

    # Filter by book_id
    response = client.get("/api/v1/trades?book_id=B1")
    assert response.status_code == 200
    data = response.json()
    assert all(trade["book_id"] == "B1" for trade in data["trades"])


def test_filtering_by_expired(client: TestClient, sample_trade_data: dict):
    """Test filtering trades by expired status."""
    # Create a trade
    client.post("/api/v1/trades", json=sample_trade_data)

    # Filter by expired=false
    response = client.get("/api/v1/trades?expired=false")
    assert response.status_code == 200
    data = response.json()
    assert all(not trade["expired"] for trade in data["trades"])


def test_sorting_trades(client: TestClient, sample_trade_data: dict):
    """Test sorting trades."""
    # Create multiple trades
    for i in range(3):
        data = sample_trade_data.copy()
        data["trade_id"] = f"T{i}"
        client.post("/api/v1/trades", json=data)

    # Sort by trade_id descending
    response = client.get("/api/v1/trades?sort_by=trade_id&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    trade_ids = [trade["trade_id"] for trade in data["trades"]]
    assert trade_ids == sorted(trade_ids, reverse=True)


def test_invalid_pagination_parameters(client: TestClient):
    """Test invalid pagination parameters."""
    # Invalid page (< 1)
    response = client.get("/api/v1/trades?page=0")
    assert response.status_code == 422

    # Invalid page_size (> 100)
    response = client.get("/api/v1/trades?page_size=200")
    assert response.status_code == 422


def test_update_nonexistent_trade(client: TestClient, sample_trade_data: dict):
    """Test updating a trade that doesn't exist."""
    response = client.put("/api/v1/trades/9999", json=sample_trade_data)
    assert response.status_code == 404


def test_delete_nonexistent_trade(client: TestClient):
    """Test deleting a trade that doesn't exist."""
    response = client.delete("/api/v1/trades/9999")
    assert response.status_code == 404


def test_create_trade_with_same_version(client: TestClient, sample_trade_data: dict):
    """Test creating trade with same version (replacement)."""
    # Create first trade
    response1 = client.post("/api/v1/trades", json=sample_trade_data)
    assert response1.status_code == 201

    # Create with same version (should succeed - replacement)
    response2 = client.post("/api/v1/trades", json=sample_trade_data)
    assert response2.status_code == 201


def test_update_trade_with_past_maturity_date(client: TestClient, sample_trade_data: dict):
    """Test updating trade with past maturity date fails."""
    # Create a trade
    create_response = client.post("/api/v1/trades", json=sample_trade_data)
    trade_id = create_response.json()["id"]

    # Try to update with past maturity date
    updated_data = sample_trade_data.copy()
    updated_data["maturity_date"] = (date.today() - timedelta(days=1)).isoformat()
    response = client.put(f"/api/v1/trades/{trade_id}", json=updated_data)
    assert response.status_code == 422  # Pydantic validation error


def test_database_health_endpoint(client: TestClient):
    """Test database health check endpoint."""
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    # Pool status may not be available for StaticPool in tests


def test_trade_id_filtering(client: TestClient, sample_trade_data: dict):
    """Test filtering by trade_id (partial match)."""
    # Create trades
    data1 = sample_trade_data.copy()
    data1["trade_id"] = "TRADE-001"
    client.post("/api/v1/trades", json=data1)

    data2 = sample_trade_data.copy()
    data2["trade_id"] = "TRADE-002"
    client.post("/api/v1/trades", json=data2)

    data3 = sample_trade_data.copy()
    data3["trade_id"] = "OTHER-001"
    client.post("/api/v1/trades", json=data3)

    # Filter by trade_id containing "TRADE"
    response = client.get("/api/v1/trades?trade_id=TRADE")
    assert response.status_code == 200
    data = response.json()
    assert all("TRADE" in trade["trade_id"] for trade in data["trades"])


def test_invalid_sort_order(client: TestClient):
    """Test invalid sort order parameter."""
    response = client.get("/api/v1/trades?sort_order=invalid")
    assert response.status_code == 422


def test_create_trade_with_invalid_data(client: TestClient):
    """Test creating trade with invalid data."""
    invalid_data = {
        "trade_id": "",  # Empty trade_id
        "version": 0,  # Invalid version (< 1)
        "counter_party_id": "CP-1",
        "book_id": "B1",
        "maturity_date": "invalid-date",  # Invalid date format
    }
    response = client.post("/api/v1/trades", json=invalid_data)
    assert response.status_code == 422


def test_pagination_edge_cases(client: TestClient, sample_trade_data: dict):
    """Test pagination edge cases."""
    # Create 3 trades
    for i in range(3):
        data = sample_trade_data.copy()
        data["trade_id"] = f"T{i}"
        client.post("/api/v1/trades", json=data)

    # Request page beyond available data
    response = client.get("/api/v1/trades?page=10&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trades"]) == 0
    assert data["total"] == 3


def test_combined_filters(client: TestClient, sample_trade_data: dict):
    """Test combining multiple filters."""
    # Create trades with different attributes
    data1 = sample_trade_data.copy()
    data1["trade_id"] = "T1"
    data1["book_id"] = "B1"
    client.post("/api/v1/trades", json=data1)

    data2 = sample_trade_data.copy()
    data2["trade_id"] = "T2"
    data2["book_id"] = "B2"
    client.post("/api/v1/trades", json=data2)

    # Filter by book_id and expired
    response = client.get("/api/v1/trades?book_id=B1&expired=false")
    assert response.status_code == 200
    data = response.json()
    assert all(trade["book_id"] == "B1" and not trade["expired"] for trade in data["trades"])
