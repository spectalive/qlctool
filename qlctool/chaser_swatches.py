"""A Chaser's tile colours: each step's, in step order, deduplicated.

A step that is itself a Chaser is read the same way; one already being read
is skipped, so a workspace whose chasers step into each other still ends.
"""

from .checks.show_graph import ShowGraph
from .max_swatches import MAX_SWATCHES
from .reach_swatches import reach_swatches


def chaser_swatches(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    chaser_id: int,
    seen: frozenset[int] = frozenset(),
) -> list[str]:
    seen = seen | {chaser_id}
    found: list[str] = []
    for step_id in graph.members.get(chaser_id, ()):
        if step_id in seen:
            continue
        step = (
            chaser_swatches(graph, groups, step_id, seen)
            if graph.kind(step_id) == "Chaser"
            else reach_swatches(graph, groups, step_id)
        )
        for colour in step:
            if colour not in found:
                found.append(colour)
            if len(found) == MAX_SWATCHES:
                return found
    return found
