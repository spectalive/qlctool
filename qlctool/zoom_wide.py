"""Open a zoom channel to its wide end, so a wash reads as a wash.

The rig had no zoom until the MAC WASH 1915Z arrived on 2026-08-29, and every
generator here reasons about colour, intensity, movement and the shutter. A
zoom channel nobody writes sits at whatever DMX 0 means on that model - on this
one, 6 degrees, a pencil - so the fixture the plot calls a wash paints a coin on
the back wall. Same shape as `shutter_open_pairs`: the looks that light a
fixture state the channel, because nothing else will.

Which end is wide comes out of the definition, never out of a model name: the
QLC+ capability presets `SmallToBig` and `BigToSmall` say which way the channel
runs, and a zoom channel that claims neither is left alone rather than guessed
at - sending 255 to a `BigToSmall` zoom is the narrow end, which is the bug this
module exists to prevent.
"""

from . import roles
from .capability import FixtureCapabilities

# Capability preset -> the end of that range that is the WIDE beam.
WIDE_END = {"SmallToBig": "maximum", "BigToSmall": "minimum"}


def zoom_wide_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, value) putting every zoom this fixture has at its widest."""
    pairs: list[tuple[int, int]] = []
    for offset, ranges in capabilities.capabilities_for_role(roles.ZOOM):
        for capability in ranges:
            end = WIDE_END.get(capability.preset)
            if end is not None:
                pairs.append((offset, getattr(capability, end)))
                break
    return pairs
