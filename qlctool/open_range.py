"""The last range on a channel that counts as its shutter open."""

from .capability import Capability

OPEN_PRESET = "ShutterOpen"


def open_range(ranges: tuple[Capability, ...]) -> Capability | None:
    """The last open range on the channel.

    Last, not first, because a shutter channel that has two of them puts one
    just above "closed" at the bottom and one at the very top; the top one is
    the one clear of the closed range, and the one the hand-built show used.
    """
    by_preset = [r for r in ranges if r.preset == OPEN_PRESET]
    if by_preset:
        return by_preset[-1]
    by_name = [r for r in ranges if r.name.strip().lower() == "open"]
    return by_name[-1] if by_name else None
