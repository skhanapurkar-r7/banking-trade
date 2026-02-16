"""Repository for trade data access operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.datetime_utils import get_current_date_utc
from app.core.exceptions import TradeNotFoundException
from app.core.logging_config import get_logger
from app.models.trade import TradeCreate, TradeUpdate
from app.repositories.database import TradeDB

logger = get_logger(__name__)


class TradeRepository:
    """
    Repository class for trade database operations.

    Handles all database interactions for trade entities.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        trade_id: Optional[str] = None,
        book_id: Optional[str] = None,
        expired: Optional[bool] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> tuple[List[TradeDB], int]:
        """
        Retrieve all trades with filtering, pagination, and sorting.
        
        Excludes soft-deleted trades.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            trade_id: Filter by trade ID (optional)
            book_id: Filter by book ID (optional)
            expired: Filter by expired status (optional)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            tuple[list[TradeDB], int]: List of trades and total count
        """
        query = self.db.query(TradeDB).filter(TradeDB.is_deleted == False)  # noqa: E712

        # Apply filters
        if trade_id:
            query = query.filter(TradeDB.trade_id.contains(trade_id))
        if book_id:
            query = query.filter(TradeDB.book_id == book_id)
        if expired is not None:
            query = query.filter(TradeDB.expired == expired)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(TradeDB, sort_by, TradeDB.id)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        trades = query.offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(trades)} trades (total: {total})")
        return trades, total

    def get_by_id(self, trade_id: int) -> Optional[TradeDB]:
        """
        Retrieve a trade by its database ID.
        
        Excludes soft-deleted trades.

        Args:
            trade_id: Database ID of the trade

        Returns:
            TradeDB | None: Trade object or None if not found
        """
        trade = (
            self.db.query(TradeDB)
            .filter(TradeDB.id == trade_id, TradeDB.is_deleted == False)  # noqa: E712
            .first()
        )
        if trade:
            logger.info(f"Retrieved trade with ID: {trade_id}")
        return trade

    def get_by_trade_id_and_version(self, trade_id: str, version: int) -> Optional[TradeDB]:
        """
        Retrieve a trade by trade ID and version.
        
        Excludes soft-deleted trades.

        Args:
            trade_id: Trade identifier
            version: Trade version number

        Returns:
            TradeDB | None: Trade object or None if not found
        """
        return (
            self.db.query(TradeDB)
            .filter(
                TradeDB.trade_id == trade_id,
                TradeDB.version == version,
                TradeDB.is_deleted == False,  # noqa: E712
            )
            .first()
        )

    def get_latest_version(self, trade_id: str) -> Optional[TradeDB]:
        """
        Get the latest version of a trade by trade ID.
        
        Excludes soft-deleted trades.

        Args:
            trade_id: Trade identifier

        Returns:
            TradeDB | None: Latest version of trade or None if not found
        """
        return (
            self.db.query(TradeDB)
            .filter(TradeDB.trade_id == trade_id, TradeDB.is_deleted == False)  # noqa: E712
            .order_by(TradeDB.version.desc())
            .first()
        )

    def create(self, trade_data: TradeCreate) -> TradeDB:
        """
        Create a new trade in the database.

        Args:
            trade_data: Trade creation data

        Returns:
            TradeDB: Created trade object
        """
        db_trade = TradeDB(
            trade_id=trade_data.trade_id,
            version=trade_data.version,
            counter_party_id=trade_data.counter_party_id,
            book_id=trade_data.book_id,
            maturity_date=trade_data.maturity_date,
            created_date=get_current_date_utc(),
            expired=trade_data.maturity_date < get_current_date_utc(),
            is_deleted=False,  # Always false for new trades
        )

        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)

        logger.info(f"Created trade: {db_trade.trade_id} v{db_trade.version}")
        return db_trade

    def update(self, trade_id: int, trade_data: TradeUpdate) -> TradeDB:
        """
        Update an existing trade.

        Args:
            trade_id: Database ID of the trade to update
            trade_data: Updated trade data

        Returns:
            TradeDB: Updated trade object

        Raises:
            TradeNotFoundException: If trade not found
        """
        db_trade = self.get_by_id(trade_id)
        if not db_trade:
            raise TradeNotFoundException(f"Trade with ID {trade_id} not found")

        # Only update fields that are provided (not None)
        if trade_data.trade_id is not None:
            db_trade.trade_id = trade_data.trade_id
        if trade_data.version is not None:
            db_trade.version = trade_data.version
        if trade_data.counter_party_id is not None:
            db_trade.counter_party_id = trade_data.counter_party_id
        if trade_data.book_id is not None:
            db_trade.book_id = trade_data.book_id
        if trade_data.maturity_date is not None:
            db_trade.maturity_date = trade_data.maturity_date
            db_trade.expired = trade_data.maturity_date < get_current_date_utc()

        self.db.commit()
        self.db.refresh(db_trade)

        logger.info(f"Updated trade: {db_trade.trade_id} v{db_trade.version}")
        return db_trade

    def delete(self, trade_id: int) -> bool:
        """
        Soft delete a trade from the database.
        
        Sets is_deleted flag to True instead of removing the record.

        Args:
            trade_id: Database ID of the trade to delete

        Returns:
            bool: True if deleted, False if not found
        """
        db_trade = self.get_by_id(trade_id)
        if not db_trade:
            return False

        db_trade.is_deleted = True
        self.db.commit()

        logger.info(f"Soft deleted trade with ID: {trade_id}")
        return True

    def update_expired_trades(self) -> int:
        """
        Update expired status for all trades with past maturity dates (UTC).
        
        Only updates non-deleted trades.

        Returns:
            int: Number of trades updated
        """
        result = (
            self.db.query(TradeDB)
            .filter(
                TradeDB.maturity_date < get_current_date_utc(),
                TradeDB.expired is False,
                TradeDB.is_deleted is False,  # Don't update deleted trades
            )
            .update({"expired": True})
        )
        self.db.commit()

        if result > 0:
            logger.info(f"Marked {result} trades as expired")
        return result
