"""A duration the description gives in seconds, as the milliseconds QLC+ counts."""

from typing import Any


def milliseconds(seconds: Any, where: str) -> int:
    """Seconds -> whole milliseconds; a ValueError for anything but a positive number."""
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds <= 0:
        raise ValueError(f"{where}: a duration is a positive number of seconds, got {seconds!r}")
    return round(seconds * 1000)
