"""Fixture ids a set of states already leaves lit with a colour."""

from .fixture_states_colour import fixture_states_colour
from .show_graph import ShowGraph, reach


def coloured_by_states(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], states: set[int]
) -> set[int]:
    coloured: set[int] = set()
    for state_id in states:
        for fixture_id, written in reach(graph, groups, state_id).items():
            if fixture_states_colour(graph.capabilities.get(fixture_id), written):
                coloured.add(fixture_id)
    return coloured
