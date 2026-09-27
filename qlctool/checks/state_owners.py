"""Family name -> every function id a room state can restore it from."""

from .families import FAMILIES
from .owner_families import owner_families
from .owner_frontier import owner_frontier
from .show_graph import ShowGraph


def state_owners(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> dict[str, set[int]]:
    families = (*FAMILIES, "pixel-mode")
    owners: dict[str, set[int]] = {family: set() for family in families}
    for state_id in states:
        for function_id in owner_frontier(graph, groups, state_id):
            for family in owner_families(graph, groups, function_id):
                owners[family].add(function_id)
    return owners
