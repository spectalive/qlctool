"""Fixture id -> the pump offsets this button raises that QLC+ will not clear."""

from ..fog_offsets import fog_offsets
from .show_graph import ShowGraph, lit, reach

# The one QLC+ zeroes every cycle. Everything else holds its last value.
RESET_GROUP = "intensity"


def pumps_held(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> dict[int, set[int]]:
    held: dict[int, set[int]] = {}
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or not capability.is_smoke:
            continue
        offsets = {
            offset
            for offset in fog_offsets(capability)
            if offset in written
            and lit(written[offset])
            and capability.groups_by_offset[offset].lower() != RESET_GROUP
        }
        if offsets:
            held[fixture_id] = offsets
    return held
