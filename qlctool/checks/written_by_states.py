"""(fixture, offset) pairs written by at least one of a set of room states."""

from .reach import reach
from .show_graph import ShowGraph


def written_by_states(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> set[tuple[int, int]]:
    owned: set[tuple[int, int]] = set()
    for state_id in states:
        for fixture_id, written in reach(graph, groups, state_id).items():
            owned.update((fixture_id, offset) for offset in written)
    return owned
