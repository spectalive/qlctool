"""Find the channel whose ranges name an off mode and an auto mode, if any."""

from .capability import Capability
from .named import named

OFF_NAMES = ("no function", "off", "no funcion")
AUTO_NAMES = ("auto",)


def mode_channel(
    channels: list[tuple[int, tuple[Capability, ...]]],
) -> tuple[int, Capability, Capability] | None:
    for offset, ranges in channels:
        off = named(ranges, OFF_NAMES)
        auto = named(ranges, AUTO_NAMES)
        if off is not None and auto is not None:
            return offset, off, auto
    return None
