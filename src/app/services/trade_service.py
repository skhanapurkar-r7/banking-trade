"""Business logic service for trade operations."""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.datetime_utils import get_current_date_utc
from app.core.exceptions import (
    MaturityDateException,
    TradeNotFoundException,
    VersionConflictException,
)
from app.core.logging_config import get_logger
from app.models.trade import Trade, TradeCreate, TradeListResponse, TradeUpdate
from app.repositories.trade_repository import TradeRepository

logger = get_logger(__name__)


class TradeService:
    """
    Service class for trade business logic.

    Implements business rules and validation for trade operations.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.repository = TradeRepository(db)

    def get_trades(
        self,
        page: int = 1,
        page_size: int = 10,
        trade_id: Optional[str] = None,
        book_id: Optional[str] = None,
        expired: Optional[bool] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> TradeListResponse:
        """
        Retrieve paginated list of trades with filtering and sorting.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            trade_id: Filter by trade ID (optional)
            book_id: Filter by book ID (optional)
            expired: Filter by expired status (optional)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            TradeListResponse: Paginated trade list with metadata
        """
        skip = (page - 1) * page_size
        trades_db, total = self.repository.get_all(
            skip=skip,
            limit=page_size,
            trade_id=trade_id,
            book_id=book_id,
            expired=expired,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        trades = [Trade.model_validate(trade) for trade in trades_db]
        total_pages = (total + page_size - 1) // page_size

        logger.info(f"Fetched page {page} of trades (total: {total})")

        return TradeListResponse(
            trades=trades, total=total, page=page, page_size=page_size, total_pages=total_pages
        )

    def get_trade(self, trade_id: int) -> Trade:
        """
        Retrieve a single trade by ID.

        Args:
            trade_id: Database ID of the trade

        Returns:
            Trade: Trade object

        Raises:
            TradeNotFoundException: If trade not found
        """
        trade_db = self.repository.get_by_id(trade_id)
        if not trade_db:
            logger.warning(f"Trade not found: {trade_id}")
            raise TradeNotFoundException(f"Trade with ID {trade_id} not found")

        return Trade.model_validate(trade_db)

    def create_trade(self, trade_data: TradeCreate) -> Trade:
        """
        Create a new trade with business rule validation.

        Business Rules:
        1. Version must be higher than existing versions for same trade_id
        2. Maturity date must not be in the past

        Args:
            trade_data: Trade creation data

        Returns:
            Trade: Created trade object

        Raises:
            VersionConflictException: If version is lower than existing
            MaturityDateException: If maturity date is in the past
        """
        # Validate maturity date
        if trade_data.maturity_date < get_current_date_utc():
            logger.warning(f"Invalid maturity date: {trade_data.maturity_date}")
            raise MaturityDateException(
                "Maturity date cannot be in the past",
                {"maturity_date": str(trade_data.maturity_date)},
            )

        # Check for existing trade with same trade_id
        existing_trade = self.repository.get_latest_version(trade_data.trade_id)

        if existing_trade:
            if trade_data.version < existing_trade.version:
                logger.warning(
                    f"Version conflict: {trade_data.version} < " f"{existing_trade.version}"
                )
                raise VersionConflictException(
                    f"Trade version {trade_data.version} is lower than "
                    f"existing version {existing_trade.version}",
                    {
                        "trade_id": trade_data.trade_id,
                        "submitted_version": trade_data.version,
                        "existing_version": existing_trade.version,
                    },
                )
            elif trade_data.version == existing_trade.version:
                # Same version - this will be handled as replacement in update
                logger.info(f"Same version detected for trade {trade_data.trade_id}")

        trade_db = self.repository.create(trade_data)
        logger.info(f"Trade created successfully: {trade_db.trade_id} v{trade_db.version}")

        return Trade.model_validate(trade_db)

    def update_trade(self, trade_id: int, trade_data: TradeUpdate) -> Trade:
        """
        Update an existing trade with validation.

        Args:
            trade_id: Database ID of the trade to update
            trade_data: Updated trade data

        Returns:
            Trade: Updated trade object

        Raises:
            TradeNotFoundException: If trade not found
            MaturityDateException: If maturity date is in the past
            VersionConflictException: If version conflict detected
        """
        # Validate maturity date if provided
        if trade_data.maturity_date is not None and trade_data.maturity_date < get_current_date_utc():
            logger.warning(f"Invalid maturity date: {trade_data.maturity_date}")
            raise MaturityDateException(
                "Maturity date cannot be in the past",
                {"maturity_date": str(trade_data.maturity_date)},
            )

        # Get existing trade
        existing_trade = self.repository.get_by_id(trade_id)
        if not existing_trade:
            raise TradeNotFoundException(f"Trade with ID {trade_id} not found")

        # Check for version conflicts with other trades if trade_id is being changed
        if trade_data.trade_id is not None and trade_data.trade_id != existing_trade.trade_id:
            latest_trade = self.repository.get_latest_version(trade_data.trade_id)
            if latest_trade and trade_data.version is not None and trade_data.version <= latest_trade.version:
                raise VersionConflictException(
                    f"Trade version {trade_data.version} conflicts with "
                    f"existing version {latest_trade.version}",
                    {
                        "trade_id": trade_data.trade_id,
                        "submitted_version": trade_data.version,
                        "existing_version": latest_trade.version,
                    },
                )

        trade_db = self.repository.update(trade_id, trade_data)
        logger.info(f"Trade updated successfully: {trade_db.trade_id} v{trade_db.version}")

        return Trade.model_validate(trade_db)

    def delete_trade(self, trade_id: int) -> bool:
        """
        Delete a trade.

        Args:
            trade_id: Database ID of the trade to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            TradeNotFoundException: If trade not found
        """
        success = self.repository.delete(trade_id)
        if not success:
            logger.warning(f"Trade not found for deletion: {trade_id}")
            raise TradeNotFoundException(f"Trade with ID {trade_id} not found")

        logger.info(f"Trade deleted successfully: {trade_id}")
        return True

    def replace_trade(self, trade_id: str, version: int, trade_data: TradeUpdate) -> Trade:
        """
        Replace an existing trade with same trade_id and version.

        Args:
            trade_id: Trade identifier
            version: Trade version
            trade_data: New trade data

        Returns:
            Trade: Updated trade object

        Raises:
            TradeNotFoundException: If trade not found
        """
        existing_trade = self.repository.get_by_trade_id_and_version(trade_id, version)
        if not existing_trade:
            raise TradeNotFoundException(f"Trade {trade_id} version {version} not found")

        return self.update_trade(existing_trade.id, trade_data)
