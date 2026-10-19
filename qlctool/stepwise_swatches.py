"""The tile colours of a function that starts a Chaser, member by member.

A Chaser's members are its steps and a Collection's run at once; either way
each member is read on its own, in order, and the colours are deduplicated.
A member that starts a Chaser is read the same way, so a Collection of
wheels shows its wheels' step colours rather than their merged maximum; any
other member keeps its merged reach. One already being read is skipped, so a
workspace whose chasers step into each other still ends.
"""

from .checks.show_graph import ShowGraph
from .max_swatches import MAX_SWATCHES
from .reach_swatches import reach_swatches
from .starts_chaser import starts_chaser


def stepwise_swatches(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    seen: frozenset[int] = frozenset(),
) -> list[str]:
    seen = seen | {function_id}
    found: list[str] = []
    for member_id in graph.members.get(function_id, ()):
        if member_id in seen:
            continue
        member = (
            stepwise_swatches(graph, groups, member_id, seen)
            if starts_chaser(graph, member_id)
            else reach_swatches(graph, groups, member_id)
        )
        for colour in member:
            if colour not in found:
                found.append(colour)
            if len(found) == MAX_SWATCHES:
                return found
    return found
