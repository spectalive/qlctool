"""A colour as the description writes it: three whole numbers 0-255."""

from typing import Any

from ...argb import RGB


def rgb_value(value: Any, where: str) -> RGB:
    """The (r, g, b) tuple, or a ValueError saying what a colour is."""
    if not (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c <= 255 for c in value)
    ):
        raise ValueError(f"{where}: a colour is three whole numbers 0-255, got {value!r}")
    return (value[0], value[1], value[2])
