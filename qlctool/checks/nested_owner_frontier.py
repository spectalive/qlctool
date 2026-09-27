"""Flatten only the multi-family level containers inside a state cycle."""

from .function_families import function_families
from .show_graph import ShowGraph
from .steps_are_levels import steps_are_levels


def nested_owner_frontier(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    inside_structural_cycle: bool,
    seen: set[int],
    level_step: bool = False,
) -> set[int]:
    if function_id in seen:
        return set()
    families = tuple(
        family
        for family, fixtures in function_families(graph, groups, function_id).items()
        if fixtures
    )
    kind = graph.kind(function_id)
    is_cycle = kind in ("Chaser", "Sequence") and (
        len(families) > 1 or steps_are_levels(graph, function_id)
    )
    is_level = (
        kind == "Collection" and inside_structural_cycle and (len(families) > 1 or level_step)
    )
    if not (is_cycle or is_level):
        return {function_id}
    nested_seen = {*seen, function_id}
    found: set[int] = set()
    for member_id in graph.members.get(function_id, ()):
        found.update(
            nested_owner_frontier(
                graph,
                groups,
                member_id,
                True,
                nested_seen,
                is_cycle and steps_are_levels(graph, function_id),
            )
        )
    return found
