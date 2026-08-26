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

from .. import roles
from ..capability import FixtureCapabilities
from ..xmlutil import find_local, findall_local

# EFXFixture::Mode - what an EFX drives on a fixture that participates in it.
EFX_PAN_TILT, EFX_DIMMER, EFX_RGB = 0, 1, 2
EFX_ROLES: dict[int, tuple[str, ...]] = {
    EFX_PAN_TILT: (roles.PAN, roles.PAN_FINE, roles.TILT, roles.TILT_FINE),
    EFX_DIMMER: (roles.DIMMER, roles.DIMMER_FINE),
    EFX_RGB: (roles.RED, roles.GREEN, roles.BLUE),
}

# What an RGBMatrix paints, and the whole of it.
MATRIX_ROLES = (roles.RED, roles.GREEN, roles.BLUE)

# A value of None means "driven, value unknown": an effect moves it around.
Driven = dict[int, dict[int, int | None]]


def driven_channels(
    function: etree._Element,
    capabilities: dict[int, FixtureCapabilities],
    group_fixtures: dict[int, tuple[int, ...]],
) -> Driven:
    """fixture id -> {offset: value or None} for one leaf function.

    Returns empty for a Chaser or a Collection: those drive nothing themselves,
    they start other functions, and the caller expands them.
    """
    kind = function.attrib.get("Type")
    if kind in ("Scene", "Sequence"):
        return _scene(function)
    if kind == "EFX":
        return _efx(function, capabilities)
    if kind == "RGBMatrix":
        return _matrix(function, capabilities, group_fixtures)
    return {}


def _scene(function: etree._Element) -> Driven:
    driven: Driven = {}
    for value in findall_local(function, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
        driven[fixture_id] = dict(zip(numbers[0::2], numbers[1::2], strict=True))
    return driven


def _efx(
    function: etree._Element, capabilities: dict[int, FixtureCapabilities]
) -> Driven:
    driven: Driven = {}
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or identifier.text is None:
            continue
        fixture_id = int(identifier.text)
        capability = capabilities.get(fixture_id)
        if capability is None:
            continue
        mode = find_local(element, "Mode")
        wanted = EFX_ROLES.get(
            int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT, ()
        )
        driven.setdefault(fixture_id, {}).update({
            offset: None
            for role in wanted
            for offset in capability.offsets_for_role(role)
        })
    return driven


def _matrix(
    function: etree._Element,
    capabilities: dict[int, FixtureCapabilities],
    group_fixtures: dict[int, tuple[int, ...]],
) -> Driven:
    group = find_local(function, "FixtureGroup")
    if group is None or group.text is None:
        return {}
    driven: Driven = {}
    for fixture_id in group_fixtures.get(int(group.text), ()):
        capability = capabilities.get(fixture_id)
        if capability is None:
            continue
        offsets = {
            offset
            for role in MATRIX_ROLES
            for offset in capability.offsets_for_role(role)
        }
        if offsets:
            driven[fixture_id] = dict.fromkeys(offsets)
    return driven
