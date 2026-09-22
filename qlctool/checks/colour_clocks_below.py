"""The chasers that rotate colour, found by shape and never by name.

A *colour clock* is a chaser at least two of whose steps state different
colours on RGB-capable fixtures - through the scenes they reach, or through
the colour an RGBMatrix paints its group. `Rueda Colores` is one; so is a
per-group mix wheel, a matrix cycle, and anything somebody builds tomorrow
that walks the room through colours on a timer. Every rule about what an
automatic colour rotation may do starts here.
"""

from .is_colour_clock import is_colour_clock
from .show_graph import ShowGraph


def colour_clocks_below(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[int]:
    """The colour clocks among this function and everything it starts."""
    return {
        member
        for member in graph.descendants(function_id)
        if graph.kind(member) == "Chaser" and is_colour_clock(graph, groups, member)
    }
