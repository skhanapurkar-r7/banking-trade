"""Trade API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    MaturityDateException,
    TradeNotFoundException,
    TradeValidationException,
    VersionConflictException,
)
from app.core.logging_config import get_logger
from app.models.trade import Trade, TradeCreate, TradeListResponse, TradeUpdate
from app.repositories.database import get_db
from app.services.trade_service import TradeService

logger = get_logger(__name__)

router = APIRouter(prefix="/trades", tags=["trades"])


def get_trade_service(db: Session = Depends(get_db)) -> TradeService:
    """
    Dependency to get trade service instance.

    Args:
        db: Database session

    Returns:
        TradeService: Trade service instance
    """
    return TradeService(db)


@router.get("", response_model=TradeListResponse)
def list_trades(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    trade_id: Optional[str] = Query(None, description="Filter by trade ID"),
    book_id: Optional[str] = Query(None, description="Filter by book ID"),
    expired: Optional[bool] = Query(None, description="Filter by expired status"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    service: TradeService = Depends(get_trade_service),
) -> TradeListResponse:
    """
    Get paginated list of trades with filtering and sorting.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        trade_id: Filter by trade ID (optional)
        book_id: Filter by book ID (optional)
        expired: Filter by expired status (optional)
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        service: Trade service instance

    Returns:
        TradeListResponse: Paginated list of trades
    """
    try:
        logger.info(f"Fetching trades: page={page}, page_size={page_size}")
        return service.get_trades(
            page=page,
            page_size=page_size,
            trade_id=trade_id,
            book_id=book_id,
            expired=expired,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch trades"
        )


@router.get("/{trade_id}", response_model=Trade)
def get_trade(trade_id: int, service: TradeService = Depends(get_trade_service)) -> Trade:
    """
    Get a single trade by ID.

    Args:
        trade_id: Database ID of the trade
        service: Trade service instance

    Returns:
        Trade: Trade object

    Raises:
        HTTPException: 404 if trade not found
    """
    try:
        logger.info(f"Fetching trade: {trade_id}")
        return service.get_trade(trade_id)
    except TradeNotFoundException as e:
        logger.warning(f"Trade not found: {trade_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching trade {trade_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch trade"
        )


@router.post("", response_model=Trade, status_code=status.HTTP_201_CREATED)
def create_trade(
    trade_data: TradeCreate, service: TradeService = Depends(get_trade_service)
) -> Trade:
    """
    Create a new trade.

    Args:
        trade_data: Trade creation data
        service: Trade service instance

    Returns:
        Trade: Created trade object

    Raises:
        HTTPException: 400 for validation errors, 409 for version conflicts
    """
    try:
        logger.info(f"Creating trade: {trade_data.trade_id} v{trade_data.version}")
        return service.create_trade(trade_data)
    except VersionConflictException as e:
        logger.warning(f"Version conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "details": e.details},
        )
    except MaturityDateException as e:
        logger.warning(f"Maturity date error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details},
        )
    except TradeValidationException as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Error creating trade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create trade"
        )


@router.put("/{trade_id}", response_model=Trade)
def update_trade(
    trade_id: int, trade_data: TradeUpdate, service: TradeService = Depends(get_trade_service)
) -> Trade:
    """
    Update an existing trade.

    Args:
        trade_id: Database ID of the trade
        trade_data: Updated trade data
        service: Trade service instance

    Returns:
        Trade: Updated trade object

    Raises:
        HTTPException: 404 if not found, 400 for validation errors, 409 for conflicts
    """
    try:
        logger.info(f"Updating trade: {trade_id}")
        return service.update_trade(trade_id, trade_data)
    except TradeNotFoundException as e:
        logger.warning(f"Trade not found: {trade_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except VersionConflictException as e:
        logger.warning(f"Version conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "details": e.details},
        )
    except MaturityDateException as e:
        logger.warning(f"Maturity date error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Error updating trade {trade_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update trade"
        )


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(trade_id: int, service: TradeService = Depends(get_trade_service)) -> None:
    """
    Delete a trade.

    Args:
        trade_id: Database ID of the trade
        service: Trade service instance

    Raises:
        HTTPException: 404 if trade not found
    """
    try:
        logger.info(f"Deleting trade: {trade_id}")
        service.delete_trade(trade_id)
    except TradeNotFoundException as e:
        logger.warning(f"Trade not found: {trade_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting trade {trade_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete trade"
        )
