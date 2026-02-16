"""Datetime utilities for consistent date/time handling across the application."""

from datetime import date, datetime, timezone


def get_current_date_utc() -> date:
    """
    Get current date in UTC timezone.

    This ensures consistent date handling across different timezones
    and is critical for financial systems where trades may be submitted
    from different geographical locations.

    Returns:
        date: Current date in UTC timezone
    """
    return datetime.now(timezone.utc).date()
