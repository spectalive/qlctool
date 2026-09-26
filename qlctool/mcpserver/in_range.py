"""A number a live tool sends to QLC+, refused before it is sent when out of range."""

from .mcp_message import mcp_message


def in_range(name: str, value: int, low: int, high: int) -> int:
    """`value`, or a ValueError naming `name` and the range."""
    if not low <= value <= high:
        raise ValueError(
            mcp_message("mcp_live_out_of_range", name=name, low=low, high=high, value=value)
        )
    return value
