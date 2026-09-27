"""The first descendant with a strobe's shape, or None if none has one."""

from .show_graph import ShowGraph
from .strobe_shape import strobe_flash_rate


def strobe_reached_from(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> int | None:
    for reached in sorted(graph.descendants(function_id)):
        if strobe_flash_rate(graph, groups, reached) is not None:
            return reached
    return None
