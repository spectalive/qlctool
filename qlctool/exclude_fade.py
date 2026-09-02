"""Tell QLC+ which channels of each patched fixture to snap instead of fade.

A `<Fixture>` in the workspace may carry `<ExcludeFade>5,6</ExcludeFade>`: the
0-based offsets QLC+ leaves out of every crossfade (`Fixture::loadXML`,
`KXMLFixtureExcludeFade`; `Fixture::channelCanFade` reads the list). The
wheels go there - see `wheel_fade_offsets` - so a chaser's fade softens the
LEDs and lets the mechanical wheels jump between detents the way they are
meant to.

Idempotent: regenerating a show rewrites the element from the definitions, so
a definition that grows a wheel is excluded the next time the show is built.
"""

from lxml import etree

from .capability import FixtureCapabilities
from .constants import QLC_NS
from .wheel_fade_offsets import wheel_fade_offsets
from .xmlutil import find_local, findall_local

TAG = "ExcludeFade"


def pin_wheel_fades(root: etree._Element, capabilities: list[FixtureCapabilities]) -> int:
    """Write the exclusion list on every fixture that has a wheel; return how many."""
    offsets_by_id = {
        capability.fixture.fixture_id: wheel_fade_offsets(capability)
        for capability in capabilities
    }
    engine = find_local(root, "Engine")
    if engine is None:
        return 0
    pinned = 0
    # Direct children only: an EFX carries <Fixture> blocks of its own.
    for fixture in findall_local(engine, "Fixture"):
        identifier = find_local(fixture, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        for stale in findall_local(fixture, TAG):
            fixture.remove(stale)
        offsets = offsets_by_id.get(int(identifier.text))
        if not offsets:
            continue
        element = etree.SubElement(fixture, f"{{{QLC_NS}}}{TAG}")
        element.text = ",".join(str(offset) for offset in offsets)
        pinned += 1
    return pinned
