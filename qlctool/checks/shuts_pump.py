"""Whether this one step writes zero to every pump offset that was raised."""

from .show_graph import ShowGraph


def shuts_pump(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], step: int, held: dict[int, set[int]]
) -> bool:
    if step not in graph.functions:
        return False
    written = graph.driven_of(graph.functions[step], groups)
    return all(
        written.get(fixture_id, {}).get(offset) == 0
        for fixture_id, offsets in held.items()
        for offset in offsets
    )
