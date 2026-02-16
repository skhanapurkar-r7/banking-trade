"""Script to seed sample trade data into the database."""

from datetime import date, timedelta

from app.core.logging_config import get_logger, setup_logging
from app.models.trade import TradeCreate
from app.repositories.database import SessionLocal, init_db
from app.services.trade_service import TradeService

setup_logging()
logger = get_logger(__name__)


def seed_trades() -> None:
    """
    Seed sample trade data into the database.
    
    Creates sample trades with various states for testing and demonstration.
    """
    logger.info("Starting database seeding...")
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    service = TradeService(db)
    
    # Sample trades
    sample_trades = [
        TradeCreate(
            trade_id="T1",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=30)
        ),
        TradeCreate(
            trade_id="T2",
            version=2,
            counter_party_id="CP-2",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=60)
        ),
        TradeCreate(
            trade_id="T2",
            version=1,
            counter_party_id="CP-1",
            book_id="B1",
            maturity_date=date.today() + timedelta(days=60)
        ),
        TradeCreate(
            trade_id="T3",
            version=3,
            counter_party_id="CP-3",
            book_id="B2",
            maturity_date=date.today() + timedelta(days=90)
        ),
        TradeCreate(
            trade_id="T4",
            version=1,
            counter_party_id="CP-4",
            book_id="B2",
            maturity_date=date.today() + timedelta(days=120)
        ),
        TradeCreate(
            trade_id="T5",
            version=1,
            counter_party_id="CP-5",
            book_id="B3",
            maturity_date=date.today() + timedelta(days=15)
        ),
    ]
    
    created_count = 0
    for trade_data in sample_trades:
        try:
            trade = service.create_trade(trade_data)
            logger.info(f"Created trade: {trade.trade_id} v{trade.version}")
            created_count += 1
        except Exception as e:
            logger.warning(f"Failed to create trade {trade_data.trade_id}: {str(e)}")
    
    db.close()
    
    logger.info(f"Seeding complete! Created {created_count} trades.")


if __name__ == "__main__":
    seed_trades()
