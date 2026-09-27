"""(fixture, offset) one function can drive, restricted to what may fight."""

from .color_roles import CONTESTED
from .show_graph import ShowGraph, reach


def contested_channels(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> dict[tuple[int, int], int | None]:
    """(fixture, offset) this function can drive, restricted to what may fight."""
    driven = reach(graph, groups, function_id)
    contested: dict[tuple[int, int], int | None] = {}
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        wanted = {offset for role in CONTESTED for offset in capability.offsets_for_role(role)}
        for offset, value in written.items():
            # A channel driven to zero everywhere is a fixture being turned
            # off, not a second opinion about its colour.
            if offset in wanted and (value is None or value > 0):
                contested[(fixture_id, offset)] = value
    return contested
