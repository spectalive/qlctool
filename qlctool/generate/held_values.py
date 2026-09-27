"""Fixture id -> every strobe channel at `fraction`, nothing else."""

from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..strobe_speed_pairs import strobe_speed_pairs
from ..workspace import Workspace


def held_values(
    workspace: Workspace, library: FixtureLibrary, fraction: float
) -> dict[int, list[tuple[int, int]]]:
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities_of(workspace.root, library):
        # A lit smoke machine strobes its LED like any PAR; the pump is not a
        # strobe channel, so nothing here can fire it (ruling D3, 2026-09-26).
        if capability.is_smoke and not capability.is_lit_smoke:
            continue
        strobing = strobe_speed_pairs(capability, fraction)
        if strobing:
            values[capability.fixture.fixture_id] = sorted(strobing)
    return values
