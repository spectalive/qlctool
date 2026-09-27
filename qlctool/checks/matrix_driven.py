"""What one RGBMatrix paints: red, green and blue on its group's heads, nothing else."""

from lxml import etree

from .. import roles
from ..find_local import find_local
from ..fixture_capabilities import FixtureCapabilities

# What an RGBMatrix paints, and the whole of it.
MATRIX_ROLES = (roles.RED, roles.GREEN, roles.BLUE)


def matrix_driven(
    function: etree._Element,
    capabilities: dict[int, FixtureCapabilities],
    group_fixtures: dict[int, tuple[int, ...]],
) -> dict[int, dict[int, int | None]]:
    group = find_local(function, "FixtureGroup")
    if group is None or group.text is None:
        return {}
    driven: dict[int, dict[int, int | None]] = {}
    for fixture_id in group_fixtures.get(int(group.text), ()):
        capability = capabilities.get(fixture_id)
        if capability is None:
            continue
        offsets = {offset for role in MATRIX_ROLES for offset in capability.offsets_for_role(role)}
        if offsets:
            driven[fixture_id] = dict.fromkeys(offsets)
    return driven
