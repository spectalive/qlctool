"""(intensity channels this step writes, whether any of them is lit).

None when the step writes no intensity channel at all - a gobo scene, a
position - which can be neither the lit nor the black half of a strobe.
"""

from .. import roles
from .reach import reach
from .show_graph import ShowGraph

INTENSITY_ROLES = (
    roles.DIMMER,
    roles.RED,
    roles.GREEN,
    roles.BLUE,
    roles.WHITE,
    roles.AMBER,
    roles.UV,
    roles.CYAN,
    roles.MAGENTA,
    roles.YELLOW,
)


def step_intensity_shape(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> tuple[frozenset[tuple[int, int]], bool] | None:
    channels: set[tuple[int, int]] = set()
    lit = False
    for fixture_id, written in reach(graph, groups, function_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        wanted = {
            offset for role in INTENSITY_ROLES for offset in capability.offsets_for_role(role)
        }
        for offset, value in written.items():
            if offset not in wanted:
                continue
            channels.add((fixture_id, offset))
            if value is None or value > 0:
                lit = True
    if not channels:
        return None
    return frozenset(channels), lit
