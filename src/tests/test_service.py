"""Tests for service layer."""

from datetime import date, timedelta

import pytest

from app.core.exceptions import (
    TradeNotFoundException,
    VersionConflictException,
)
from app.models.trade import TradeCreate, TradeUpdate
from app.repositories.database import TradeDB
from app.services.trade_service import TradeService


def test_get_trades_with_filters(db_session):
    """Test getting trades with various filters."""
    service = TradeService(db_session)

    # Create test trades
    trade1 = TradeDB(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
        created_date=date.today(),
        expired=False,
    )
    trade2 = TradeDB(
        trade_id="T2",
        version=1,
        counter_party_id="CP-2",
        book_id="B2",
        maturity_date=date.today() + timedelta(days=60),
        created_date=date.today(),
        expired=False,
    )
    db_session.add_all([trade1, trade2])
    db_session.commit()

    # Test filtering by book_id
    result = service.get_trades(book_id="B1")
    assert result.total == 1
    assert result.trades[0].book_id == "B1"


def test_get_trade_not_found(db_session):
    """Test getting non-existent trade raises exception."""
    service = TradeService(db_session)

    with pytest.raises(TradeNotFoundException):
        service.get_trade(9999)


def test_create_trade_with_lower_version(db_session):
    """Test creating trade with lower version raises exception."""
    service = TradeService(db_session)

    # Create initial trade
    trade_data = TradeCreate(
        trade_id="T1",
        version=2,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )
    service.create_trade(trade_data)

    # Try to create with lower version
    lower_version_data = TradeCreate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )

    with pytest.raises(VersionConflictException):
        service.create_trade(lower_version_data)


def test_create_trade_with_higher_version(db_session):
    """Test creating trade with higher version succeeds."""
    service = TradeService(db_session)

    # Create initial trade
    trade_data = TradeCreate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )
    service.create_trade(trade_data)

    # Create with higher version
    higher_version_data = TradeCreate(
        trade_id="T1",
        version=2,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )

    result = service.create_trade(higher_version_data)
    assert result.version == 2


def test_create_trade_with_past_maturity_date(db_session):
    """Test creating trade with past maturity date raises exception."""
    # Pydantic validation will catch this before service layer
    # So we test that the validation works
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TradeCreate(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() - timedelta(days=1),
        )


def test_update_trade_not_found(db_session):
    """Test updating non-existent trade raises exception."""
    service = TradeService(db_session)

    trade_data = TradeUpdate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )

    with pytest.raises(TradeNotFoundException):
        service.update_trade(9999, trade_data)


def test_update_trade_with_past_maturity_date(db_session):
    """Test updating trade with past maturity date raises exception."""
    # Create a trade
    trade = TradeDB(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
        created_date=date.today(),
        expired=False,
    )
    db_session.add(trade)
    db_session.commit()

    # Pydantic validation will catch this
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TradeUpdate(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() - timedelta(days=1),
        )


def test_update_trade_success(db_session):
    """Test successful trade update."""
    service = TradeService(db_session)

    # Create two trades with same trade_id
    trade1 = TradeDB(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
        created_date=date.today(),
        expired=False,
    )
    db_session.add(trade1)
    db_session.commit()

    # Update trade successfully
    update_data = TradeUpdate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-2",
        book_id="B2",
        maturity_date=date.today() + timedelta(days=60),
    )

    result = service.update_trade(trade1.id, update_data)
    assert result.counter_party_id == "CP-2"
    assert result.book_id == "B2"


def test_delete_trade_not_found(db_session):
    """Test deleting non-existent trade raises exception."""
    service = TradeService(db_session)

    with pytest.raises(TradeNotFoundException):
        service.delete_trade(9999)


def test_delete_trade_success(db_session):
    """Test successful trade deletion."""
    service = TradeService(db_session)

    # Create a trade
    trade = TradeDB(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
        created_date=date.today(),
        expired=False,
    )
    db_session.add(trade)
    db_session.commit()
    trade_id = trade.id

    # Delete the trade
    result = service.delete_trade(trade_id)
    assert result is True

    # Verify it's deleted
    with pytest.raises(TradeNotFoundException):
        service.get_trade(trade_id)


def test_get_trades_pagination(db_session):
    """Test pagination of trades."""
    service = TradeService(db_session)

    # Create 5 trades
    for i in range(5):
        trade = TradeDB(
            trade_id=f"T{i}",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False,
        )
        db_session.add(trade)
    db_session.commit()

    # Get first page
    result = service.get_trades(page=1, page_size=2)
    assert len(result.trades) == 2
    assert result.total == 5
    assert result.total_pages == 3

    # Get second page
    result = service.get_trades(page=2, page_size=2)
    assert len(result.trades) == 2

    # Get last page
    result = service.get_trades(page=3, page_size=2)
    assert len(result.trades) == 1


def test_get_trades_sorting(db_session):
    """Test sorting of trades."""
    service = TradeService(db_session)

    # Create trades with different trade_ids
    for i in [3, 1, 2]:
        trade = TradeDB(
            trade_id=f"T{i}",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30),
            created_date=date.today(),
            expired=False,
        )
        db_session.add(trade)
    db_session.commit()

    # Sort ascending
    result = service.get_trades(sort_by="trade_id", sort_order="asc")
    trade_ids = [t.trade_id for t in result.trades]
    assert trade_ids == ["T1", "T2", "T3"]

    # Sort descending
    result = service.get_trades(sort_by="trade_id", sort_order="desc")
    trade_ids = [t.trade_id for t in result.trades]
    assert trade_ids == ["T3", "T2", "T1"]


def test_replace_trade_not_found(db_session):
    """Test replacing non-existent trade raises exception."""
    service = TradeService(db_session)

    trade_data = TradeUpdate(
        trade_id="T1",
        version=1,
        counter_party_id="CP-1",
        book_id="B1",
        maturity_date=date.today() + timedelta(days=30),
    )

    with pytest.raises(TradeNotFoundException):
        service.replace_trade("T1", 1, trade_data)
