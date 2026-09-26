"""Whether a value written on a strobe-role channel shuts the fixture.

A strobe-role channel means two different things. On a LED PAR it is only a
strobe: 0 is "no strobe", the light stays as it is. On a MiN Wash it is the
fixture's whole intensity, "Dimmer/Strobe", and 0 is "Closed": the wash goes
dark. The definition says which, and the name of a channel does not.

A value shuts when the channel has labelled ranges and the range the value
falls in is neither open nor strobing: not the open range `shutter_open_ranges`
finds, not the strobe range, and not labelled open, lamp on or "no strobe". A
bare speed channel (no labelled ranges) never shuts: 0 there is no strobe.
"""

from ..capability import FixtureCapabilities
from ..shutter_open import shutter_open_ranges
from ..strobe_range import strobe_range

OPEN_PRESETS = ("ShutterOpen", "LampOn")
OPEN_WORDS = ("open", "no strobe")


def value_shuts(capability: FixtureCapabilities, offset: int, value: int) -> bool:
    ranges = capability.capabilities_by_offset[offset]
    if not ranges:
        return False
    strobing = strobe_range(ranges)
    if strobing is not None and strobing.minimum <= value <= strobing.maximum:
        return False
    opening = dict(shutter_open_ranges(capability)).get(offset)
    if opening is not None and opening.minimum <= value <= opening.maximum:
        return False
    for labelled in ranges:
        if not labelled.minimum <= value <= labelled.maximum:
            continue
        name = labelled.name.strip().lower()
        if (labelled.preset or "") in OPEN_PRESETS or any(w in name for w in OPEN_WORDS):
            return False
    return True
