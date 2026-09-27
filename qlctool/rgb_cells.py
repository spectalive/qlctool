"""The fixtures an RGBMatrix can be seen on: red, green and blue, or cyan, magenta, yellow.

A matrix in RGB mode writes a head's red, green and blue, and on a head with
no such triple falls back to its cyan, magenta and yellow
(qlcplus engine/src/rgbmatrix.cpp, RGBMatrix::updateMapChannels). A cell with
neither triple - a 7R beam on a colour wheel - shows no matrix at all, however
the grid is drawn. The CMY fallback was missing until the Round 2 review of
2026-09-27; `checks/driven_channels` still reads RGB only.
"""

from collections.abc import Iterable, Mapping

from . import roles
from .fixture_capabilities import FixtureCapabilities


def rgb_cells(
    capabilities: Mapping[int, FixtureCapabilities], fixture_ids: Iterable[int]
) -> list[int]:
    """The `fixture_ids`, in order, whose fixture has red, green and blue, or cyan, magenta, yellow."""
    return [
        fixture_id
        for fixture_id in fixture_ids
        if (capability := capabilities.get(fixture_id)) is not None
        and any(
            all(capability.has_role(role) for role in triple)
            for triple in (
                (roles.RED, roles.GREEN, roles.BLUE),
                (roles.CYAN, roles.MAGENTA, roles.YELLOW),
            )
        )
    ]
