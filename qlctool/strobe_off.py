"""The value that stops a strobe-only channel, for the scenes that own the light.

`shutter_open_pairs` parks every shutter that has an "open" range to park it
in, and deliberately leaves alone the channels that are only a strobe - on
those, untouched already means off. That held until the Flash buttons: a flash
writes the strobing value while held, and a strobe channel is LTP, so release
restores nothing. The panels, the PC-64s and the mini heads strobed until
somebody found `Strobo OFF` by hand (owner, 2026-08-28, "se queda el estrobo
para siempre") - because unlike the wash heads, no scene lighting them ever
wrote their strobe channel back.

So the scenes that claim a fixture's light also claim its strobe-only
channels, at the value that stops them: zero on a bare speed channel, zero on
a ranged channel whose strobing starts above it. A channel `shutter_open`
already parks is left to it, and a channel that strobes at zero has no off
value to write and is left alone.
"""

from . import roles
from .capability import FixtureCapabilities
from .shutter_open import shutter_open_ranges
from .strobe_range import strobe_range


def strobe_off_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, 0) for every strobe-only channel zero actually stops."""
    opened = {offset for offset, _ in shutter_open_ranges(capabilities)}
    pairs: list[tuple[int, int]] = []
    for offset, ranges in capabilities.capabilities_for_role(roles.STROBE):
        if offset in opened:
            continue
        if not ranges:
            pairs.append((offset, 0))
            continue
        strobing = strobe_range(ranges)
        if strobing is not None and strobing.minimum > 0:
            pairs.append((offset, 0))
    return pairs
