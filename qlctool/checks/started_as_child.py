"""A branching function that a room state other than itself reaches."""

from .show_graph import BRANCHING, ShowGraph


def started_as_child(
    graph: ShowGraph, reached: dict[int, frozenset[int]], function_id: int
) -> bool:
    if graph.kind(function_id) not in BRANCHING:
        return False
    return any(
        function_id in below for state_id, below in reached.items() if state_id != function_id
    )
