"""Every (fixture, offset) a function can drive, through anything it starts."""

from ..checks.reach import reach
from ..checks.show_graph import ShowGraph


def written_channels(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> frozenset[tuple[int, int]]:
    """The channels `function_id` reaches, as (fixture id, offset) pairs."""
    return frozenset(
        (fixture_id, offset)
        for fixture_id, pairs in reach(graph, groups, function_id).items()
        for offset in pairs
    )
