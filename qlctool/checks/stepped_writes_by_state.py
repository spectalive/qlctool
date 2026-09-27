"""(fixture, offset) -> the states whose chasers re-write it at a step."""

from .show_graph import ShowGraph
from .stepped_leaves import stepped_leaves


def stepped_writes_by_state(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> dict[tuple[int, int], set[int]]:
    """(fixture, offset) -> the states whose chasers re-write it at a step."""
    found: dict[tuple[int, int], set[int]] = {}
    for state_id in states:
        for leaf_id in stepped_leaves(graph, state_id):
            leaf = graph.functions.get(leaf_id)
            if leaf is None:
                continue
            for fixture_id, written in graph.driven_of(leaf, groups).items():
                for offset in written:
                    found.setdefault((fixture_id, offset), set()).add(state_id)
    return found
