"""Fixture id -> (values that strobe it, values that reopen it).

The strobing value through `strobe_speed_pairs`, which also covers the
channels whose whole job is the strobe and carry no labelled range at all
(the Vortex PC-64, the HYULIGHTS panels) - leaving those out is how
`Strobo ON` shipped strobing ten fixtures and skipping nine (found live,
2026-08-27). The reopen value through `shutter_open_pairs`, so a strobe
that stops and a scene that opens a shutter always agree on where "open"
is; a channel with no labelled open position reopens at 0, which is where
the untouched channel already sat.
"""

from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..shutter_open import shutter_open_pairs
from ..strobe_speed_pairs import strobe_speed_pairs
from ..workspace import Workspace

ON_FRACTION = 0.5


def shutter_values(
    workspace: Workspace, library: FixtureLibrary
) -> dict[int, tuple[list[tuple[int, int]], list[tuple[int, int]]]]:
    result: dict[int, tuple[list[tuple[int, int]], list[tuple[int, int]]]] = {}
    for capability in capabilities_of(workspace.root, library):
        if capability.is_smoke and not capability.is_lit_smoke:
            continue
        reopen = dict(shutter_open_pairs(capability))
        strobing = strobe_speed_pairs(capability, ON_FRACTION)
        opening = [(offset, reopen.get(offset, 0)) for offset, _ in strobing]
        if strobing:
            result[capability.fixture.fixture_id] = (strobing, opening)
    return result
