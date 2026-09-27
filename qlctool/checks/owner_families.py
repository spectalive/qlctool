"""Every family a direct functional state owner can restore."""

from .function_families import function_families
from .show_graph import ShowGraph
from .steps_are_levels import steps_are_levels


def owner_families(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> tuple[str, ...]:
    families = tuple(
        family
        for family, fixtures in function_families(graph, groups, function_id).items()
        if fixtures
    )
    if graph.kind(function_id) in ("Chaser", "Sequence") and (
        len(families) > 1 or steps_are_levels(graph, function_id)
    ):
        return ()
    return families
