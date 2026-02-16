"""Background scheduler for periodic tasks."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging_config import get_logger
from app.repositories.database import SessionLocal
from app.repositories.trade_repository import TradeRepository

logger = get_logger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def update_expired_trades_job():
    """
    Background job to update expired trades.

    Runs daily at midnight UTC to mark trades as expired
    when their maturity date has passed.
    """
    logger.info("Running scheduled expiry update job...")

    db = SessionLocal()
    try:
        repository = TradeRepository(db)
        count = repository.update_expired_trades()

        if count > 0:
            logger.info(f"Scheduled job: Marked {count} trades as expired")
        else:
            logger.info("Scheduled job: No trades to expire")
    except Exception as e:
        logger.error(f"Error in scheduled expiry update: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler with all scheduled jobs.

    Jobs:
    - update_expired_trades_job: Runs daily at midnight UTC
    """
    if not scheduler.running:
        # Schedule expiry update job to run daily at midnight UTC
        scheduler.add_job(
            update_expired_trades_job,
            trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
            id="update_expired_trades",
            name="Update Expired Trades",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("Background scheduler started - Expiry job scheduled for midnight UTC")
    else:
        logger.warning("Scheduler is already running")


def shutdown_scheduler():
    """
    Shutdown the background scheduler gracefully.

    Should be called on application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Background scheduler shut down")
