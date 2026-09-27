"""The fixtures whose pan or tilt a button animates through an EFX."""

from .efx_moves_pan_tilt import efx_moves_pan_tilt
from .show_graph import ShowGraph
from .writes_pan_or_tilt import writes_pan_or_tilt


def pan_tilt_moved_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[int]:
    moved: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or not efx_moves_pan_tilt(function):
            continue
        for fixture_id, pairs in graph.driven_of(function, groups).items():
            if writes_pan_or_tilt(graph, fixture_id, pairs):
                moved.add(fixture_id)
    return moved
