"""The fixtures an RGBMatrix can be seen on: the ones with red, green and blue.

A matrix writes red, green and blue onto the cells of its group and nothing
else (`checks/driven_channels`), so a cell without all three - a 7R beam on a
colour wheel - shows no matrix at all, however the grid is drawn.
"""

from collections.abc import Iterable, Mapping

from . import roles
from .capability import FixtureCapabilities


def rgb_cells(
    capabilities: Mapping[int, FixtureCapabilities], fixture_ids: Iterable[int]
) -> list[int]:
    """The `fixture_ids`, in order, whose fixture has red, green and blue."""
    return [
        fixture_id
        for fixture_id in fixture_ids
        if (capability := capabilities.get(fixture_id)) is not None
        and all(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]
