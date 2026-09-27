"""(fixture, offset) -> definite dimmer values the member's scenes state.

Only Scenes: an EFX in dimmer mode writes values nobody can predict, and a
matrix never touches a dimmer at all. Zeroes are skipped - a member turning
a fixture off is not a second opinion about how bright it should be.
"""

from .. import roles
from .show_graph import ShowGraph

LEAVES = ("Scene", "Sequence")


def dimmer_value_writes(graph: ShowGraph, function_id: int) -> dict[tuple[int, int], set[int]]:
    writes: dict[tuple[int, int], set[int]] = {}
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") not in LEAVES:
            continue
        for fixture_id, pairs in graph.driven_of(function, {}).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            dimmers = set(capability.offsets_for_role(roles.DIMMER))
            for offset, value in pairs.items():
                if offset in dimmers and value is not None and value > 0:
                    writes.setdefault((fixture_id, offset), set()).add(value)
    return writes
