"""Common schema utilities."""

from datetime import datetime, timezone
import uuid


def gen_id() -> str:
    """Generate a unique identifier."""

    return str(uuid.uuid4())


def utc_now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""

    return datetime.now(timezone.utc).isoformat()