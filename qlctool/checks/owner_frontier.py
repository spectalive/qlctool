"""Functions whose starts can return one family to its room-state owner.

A multi-family Chaser/Sequence coordinates structural level Collections;
recurse through those until one family has its actual owner. A single-family
Collection or Chaser such as `Movimientos Suaves` or `Gobo Animacion`
remains the functional owner, never its leaf steps. A Chaser whose steps
are all level Collections is structural too, even with one family
(`steps_are_levels`, 2026-09-25). A static floor the state starts under
its hooks (`static_floors`) owns nothing: it is what a released pick lands
on, and the frame's hooks still own the family (2026-09-27, ruling D8).
"""

from .nested_owner_frontier import nested_owner_frontier
from .show_graph import ShowGraph
from .static_floors import static_floors


def owner_frontier(graph: ShowGraph, groups: dict[int, tuple[int, ...]], state_id: int) -> set[int]:
    found: set[int] = set()
    floors = static_floors(graph, groups, state_id, (state_id,))
    for function_id in graph.members.get(state_id, ()):
        if function_id in floors:
            continue
        found.update(nested_owner_frontier(graph, groups, function_id, False, set()))
    return found
