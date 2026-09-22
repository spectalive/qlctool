"""The distinct colours one step of a chaser puts on the room, as the eye counts them.

Every RGB fixture's colour is put back together by `fixture_colour` before it
is compared, and a matrix contributes the colour it paints. Fixtures whose
colour is a wheel are not counted: a wheel has fifteen detents and the palette
seventeen colours, so a beam on "the nearest position" is never the same
value as the wash beside it even when it is the same colour.
"""

from ..argb import rgb_from_argb
from .driven_channels import driven_channels
from .fixture_colour import fixture_colour
from .matrix_colour import matrix_colour
from .show_graph import ShowGraph


def step_palette(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], step_id: int
) -> set[tuple[int, int, int]]:
    """Every distinct lit colour this step puts on an RGB fixture or a matrix."""
    colours: set[tuple[int, int, int]] = set()
    for member in graph.descendants(step_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        kind = function.attrib.get("Type")
        if kind in ("Scene", "Sequence"):
            for fixture_id, written in driven_channels(function, graph.capabilities, {}).items():
                colour = fixture_colour(graph, fixture_id, written)
                if colour is not None and any(colour):
                    colours.add(colour)
        elif kind == "RGBMatrix":
            argb = matrix_colour(function)
            if argb is not None:
                rgb = rgb_from_argb(argb)
                if any(rgb):
                    colours.add(rgb)
    return colours
