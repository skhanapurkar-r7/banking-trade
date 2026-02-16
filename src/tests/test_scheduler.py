"""Tests for scheduler functionality."""

from unittest.mock import patch

import pytest

from app.core.scheduler import shutdown_scheduler, start_scheduler, update_expired_trades_job


def test_update_expired_trades_job_basic():
    """Test the scheduled expiry update job runs without error."""
    # Just test that the job can be called without raising exceptions
    try:
        update_expired_trades_job()
    except Exception as e:
        pytest.fail(f"Job should not raise exception: {e}")


def test_update_expired_trades_job_no_trades_basic():
    """Test expiry job when no trades exist."""
    # Just test that the job can be called without raising exceptions
    try:
        update_expired_trades_job()
    except Exception as e:
        pytest.fail(f"Job should not raise exception: {e}")


def test_update_expired_trades_job_error_handling(db_session):
    """Test expiry job handles errors gracefully."""
    # Mock SessionLocal to raise an exception
    with patch("app.core.scheduler.SessionLocal") as mock_session:
        mock_session.return_value.__enter__.side_effect = Exception("Database error")

        # Job should not raise exception
        try:
            update_expired_trades_job()
        except Exception:
            pytest.fail("Job should handle exceptions gracefully")


def test_start_scheduler():
    """Test starting the scheduler."""
    with patch("app.core.scheduler.scheduler") as mock_scheduler:
        mock_scheduler.running = False

        start_scheduler()

        # Verify scheduler was started
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()


def test_start_scheduler_already_running():
    """Test starting scheduler when already running."""
    with patch("app.core.scheduler.scheduler") as mock_scheduler:
        mock_scheduler.running = True

        start_scheduler()

        # Verify scheduler was not started again
        mock_scheduler.start.assert_not_called()


def test_shutdown_scheduler():
    """Test shutting down the scheduler."""
    with patch("app.core.scheduler.scheduler") as mock_scheduler:
        mock_scheduler.running = True

        shutdown_scheduler()

        # Verify scheduler was shut down
        mock_scheduler.shutdown.assert_called_once_with(wait=True)


def test_shutdown_scheduler_not_running():
    """Test shutting down scheduler when not running."""
    with patch("app.core.scheduler.scheduler") as mock_scheduler:
        mock_scheduler.running = False

        shutdown_scheduler()

        # Verify shutdown was not called
        mock_scheduler.shutdown.assert_not_called()


def test_scheduler_job_configuration():
    """Test scheduler job is configured correctly."""
    with patch("app.core.scheduler.scheduler") as mock_scheduler:
        mock_scheduler.running = False

        start_scheduler()

        # Verify job configuration
        call_args = mock_scheduler.add_job.call_args
        assert call_args[0][0] == update_expired_trades_job
        assert call_args[1]["id"] == "update_expired_trades"
        assert call_args[1]["name"] == "Update Expired Trades"
        assert call_args[1]["replace_existing"] is True
