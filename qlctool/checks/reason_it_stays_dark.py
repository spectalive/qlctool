"""Whether a fixture's dimmer or shutter is the reason it stays dark."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..shutter_open_ranges import shutter_open_ranges
from ..strobe_range import strobe_range
from .lit import lit
from .shutter_off_range import shutter_off_range

# What a DMX channel reads as when no function has written to it.
UNTOUCHED = 0


def reason_it_stays_dark(capability: FixtureCapabilities, written: dict[int, int | None]) -> bool:
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers and not any(lit(written.get(o, 0)) for o in dimmers):
        return True
    return any(
        shutter_off_range(
            written.get(offset, UNTOUCHED),
            opening,
            strobe_range(capability.capabilities_by_offset[offset]),
        )
        for offset, opening in shutter_open_ranges(capability)
    )
