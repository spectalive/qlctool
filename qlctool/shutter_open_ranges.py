"""(offset, the open range) for every shutter a fixture has."""

from . import roles
from .definition import Capability
from .fixture_capabilities import FixtureCapabilities
from .open_range import open_range


def shutter_open_ranges(
    capabilities: FixtureCapabilities,
) -> list[tuple[int, Capability]]:
    """(offset, the range that counts as open) for every shutter it has.

    The range, not just a value, because whether a fixture is open depends on
    where its shutter *is*, not on whether anybody wrote to it. A CLB2.4 head
    labels DMX 0 "no strobe", so an untouched channel is already open; a BEAM
    230W 7R puts open near the top, so an untouched channel is shut. Only the
    range can tell those apart, and getting it wrong is either a fixture
    reported dark that is fine or a fixture dark that nobody warned about.
    """
    found: list[tuple[int, Capability]] = []
    for offset, ranges in capabilities.capabilities_for_role(roles.STROBE):
        opening = open_range(ranges)
        if opening is not None:
            found.append((offset, opening))
    return found
