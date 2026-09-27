"""Whether any value in a set of channels is lit."""

from .show_graph import lit


def channels_any_lit(channels: dict[int, int | None]) -> bool:
    return any(lit(value) for value in channels.values())
