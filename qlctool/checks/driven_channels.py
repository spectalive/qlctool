"""Which channels one function actually drives, and to what.

Every check downstream asks the same question in a different way - is anything
opening this dimmer, is anything else writing this colour - and all of them need
this first: given a leaf function, which (fixture, offset) does it touch, and
what value does it put there when that is knowable.

The three leaf kinds hide the trap the show kept falling into. A Scene says
exactly what it writes. An **EFX** writes pan/tilt, or the dimmer, or RGB
depending on each fixture's `<Mode>`, and never says a value. An **RGBMatrix**
writes red, green and blue onto the heads of one fixture group and *nothing
else* - not the master dimmer, not the shutter - which is why a panel with a
dimmer on channel 1 goes dark under a matrix that is painting it beautifully.
"""

from lxml import etree

from ..fixture_capabilities import FixtureCapabilities
from .efx_driven import efx_driven
from .matrix_driven import matrix_driven
from .scene_driven import scene_driven

# A value of None means "driven, value unknown": an effect moves it around.
Driven = dict[int, dict[int, int | None]]


def driven_channels(
    function: etree._Element,
    capabilities: dict[int, FixtureCapabilities],
    group_fixtures: dict[int, tuple[int, ...]],
) -> Driven:
    """Fixture id -> {offset: value or None} for one leaf function.

    Returns empty for a Chaser or a Collection: those drive nothing themselves,
    they start other functions, and the caller expands them.
    """
    kind = function.attrib.get("Type")
    if kind in ("Scene", "Sequence"):
        return scene_driven(function)
    if kind == "EFX":
        return efx_driven(function, capabilities)
    if kind == "RGBMatrix":
        return matrix_driven(function, capabilities, group_fixtures)
    return {}
