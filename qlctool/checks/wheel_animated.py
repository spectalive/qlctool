"""Either a rotation range, or more than one detent across the look."""

from .. import roles
from .offset_in_rotation_range import offset_in_rotation_range
from .show_graph import ShowGraph


def wheel_animated(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int, fixture_id: int
) -> bool:
    capability = graph.capabilities[fixture_id]
    offsets = set(capability.offsets_for_role(roles.COLOR_MACRO))
    seen: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        pairs = graph.driven_of(function, groups).get(fixture_id, {})
        for offset in offsets & set(pairs):
            value = pairs[offset]
            if value is None:  # an effect on the wheel itself: unpredictable, so moving
                return True
            if offset_in_rotation_range(capability, offset, value):
                return True
            seen.add(value)
    return len(seen) > 1
