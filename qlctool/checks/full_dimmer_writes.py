"""(fixture, offset) dimmer channels a Scene under this branch holds at 255."""

from .. import roles
from .show_graph import ShowGraph

FULL = 255


def full_dimmer_writes(graph: ShowGraph, function_id: int) -> set[tuple[int, int]]:
    channels: set[tuple[int, int]] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") not in ("Scene", "Sequence"):
            continue
        for fixture_id, pairs in graph.driven_of(function, {}).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            channels |= {
                (fixture_id, offset)
                for offset, value in pairs.items()
                if offset in dimmers and value == FULL
            }
    return channels
