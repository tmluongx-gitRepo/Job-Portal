"""Utility functions for datetime operations."""

from datetime import UTC, datetime


def ensure_utc_datetime(dt: datetime | None) -> datetime | None:
    """
    Ensure a datetime object is timezone-aware and in UTC.

    Args:
        dt: A datetime object (may be naive or aware)

    Returns:
        A timezone-aware datetime in UTC, or None if input is None

    Note:
        - If dt is naive, it's assumed to be in UTC and tzinfo is added
        - If dt is aware but not UTC, it's converted to UTC
        - This prevents "can't compare offset-naive and offset-aware datetimes" errors
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        # Naive datetime - assume UTC and make it aware
        return dt.replace(tzinfo=UTC)

    # Already aware - convert to UTC if needed
    return dt.astimezone(UTC)
