"""The rigged fixtures that mix colour and belong to no fixture group.

A colour bank is one group's, so these get none: the two CLB2.4 PARs and the
four fog LED columns stayed on the old colour while a bank key held the rest of
the rig (en-sala DMX audit, 2026-09-26). A smoke machine joins only when it
carries lights; its pump is never a colour (`color_scene_values`).
"""

from collections.abc import Sequence

from lxml import etree

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..fixture_group import fixture_groups
from ..rigged_fixture_ids import rigged_fixture_ids


def ungrouped_colour_fixture_ids(
    root: etree._Element, capabilities: Sequence[FixtureCapabilities]
) -> list[int]:
    """Their fixture ids, in patch order."""
    grouped = {f for group in fixture_groups(root) for f in group.fixture_ids}
    rigged = rigged_fixture_ids(root)
    return [
        caps.fixture.fixture_id
        for caps in capabilities
        if caps.fixture.fixture_id in rigged
        and caps.fixture.fixture_id not in grouped
        and not (caps.is_smoke and not caps.is_lit_smoke)
        and any(caps.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
