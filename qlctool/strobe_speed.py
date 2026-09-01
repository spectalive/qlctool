"""A value that makes each of a fixture's strobe channels actually strobe.

`fraction` is where to sit on the channel's slow-to-fast run: 0.0 is its
slowest strobe, 1.0 its fastest. Two kinds of channel answer it:

- A channel with a labelled strobing range (found by `strobe_range`) gets a
  value inside that range - never outside it, because the neighbouring ranges
  are "Open", "Closed" and "No function", the values that do anything but
  strobe.
- A channel whose *whole job* is the strobe - role `strobe`, but not one
  labelled range on it (the Vortex PC-64's channel 5, the HYULIGHTS panels'
  channel 5) - is read as speed across its full 0-255 run. That is not a
  guess: the hand-built show drove exactly these channels at 250/255 for its
  fast flash and 220/140 for its slow one, every gig for years.

A strobe-role channel that has labels but none of them strobing (nothing here
today) is skipped: writing it would be the guess this toolkit exists to avoid.
"""

from . import roles
from .capability import FixtureCapabilities
from .strobe_range import strobe_range


def strobe_speed_pairs(capabilities: FixtureCapabilities, fraction: float) -> list[tuple[int, int]]:
    """(offset, value) strobing every strobe channel this fixture has."""
    pairs: list[tuple[int, int]] = []
    for offset, ranges in capabilities.capabilities_for_role(roles.STROBE):
        if not ranges:
            pairs.append((offset, round(fraction * 255)))
            continue
        strobing = strobe_range(ranges)
        if strobing is None:
            continue
        span = strobing.maximum - strobing.minimum
        pairs.append((offset, strobing.minimum + round(fraction * span)))
    return pairs
