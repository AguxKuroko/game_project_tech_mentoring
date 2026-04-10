from datetime import UTC, datetime


def get_time() -> datetime:
    """Return the current UTC timestamp as a datetime object."""
    return datetime.now(UTC)
