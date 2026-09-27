"""Which channels of each patched fixture QLC+ merges highest-takes-precedence.

`Universe::setChannelCapability` marks a channel HTP when its group is
Intensity, unless the patch lists it under the fixture's `<ForcedLTP>`, and
also when the patch lists it under `<ForcedHTP>`. On an HTP channel
`Universe::write` drops any value lower than the one already there, unless the
writer forces LTP - which is the whole difference between a held strobe that
shows and one the running level out-bids.
"""

from collections.abc import Mapping

from lxml import etree

from ..fixture_capabilities import FixtureCapabilities
from ..xmlutil import find_local, iter_local

INTENSITY_GROUP = "Intensity"


def htp_offsets(
    root: etree._Element, capabilities: Mapping[int, FixtureCapabilities]
) -> dict[int, frozenset[int]]:
    """Fixture id -> the offsets merged HTP, as the patch leaves them."""
    forced: dict[int, dict[str, set[int]]] = {}
    for element in iter_local(root, "Fixture"):
        identifier = find_local(element, "ID")
        if find_local(element, "Channels") is None or identifier is None or not identifier.text:
            continue
        lists = forced.setdefault(int(identifier.text), {})
        for kind in ("ForcedLTP", "ForcedHTP"):
            listed = find_local(element, kind)
            text = (listed.text or "") if listed is not None else ""
            lists[kind] = {int(n) for n in text.split(",") if n.strip().isdigit()}
    found: dict[int, frozenset[int]] = {}
    for fixture_id, capability in capabilities.items():
        lists = forced.get(fixture_id, {})
        intensity = {
            offset
            for offset, group in enumerate(capability.groups_by_offset)
            if group == INTENSITY_GROUP
        }
        found[fixture_id] = frozenset(
            (intensity - lists.get("ForcedLTP", set())) | lists.get("ForcedHTP", set())
        )
    return found
