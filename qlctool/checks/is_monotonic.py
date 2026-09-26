"""Whether a row of values only rises or only falls."""

from collections.abc import Sequence


def is_monotonic(values: Sequence[int]) -> bool:
    """True when `values` never turn back: all rising or all falling."""
    return list(values) == sorted(values) or list(values) == sorted(values, reverse=True)
