"""The fixtures one step of a chaser puts on white, by name.

White by RGB, white by wheel detent, or white by a matrix painting its group
pure white - the three ways the file can say it.
"""

from ..argb import rgb_from_argb
from .detent_white import detent_white
from .matrix_colour import matrix_colour
from .rgb_white import rgb_white
from .show_graph import ShowGraph

WHITE = (255, 255, 255)


def white_fixtures(graph: ShowGraph, groups: dict[int, tuple[int, ...]], step_id: int) -> set[str]:
    names: set[str] = set()
    for member in graph.descendants(step_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        kind = function.attrib.get("Type")
        if kind in ("Scene", "Sequence"):
            for fixture_id, written in graph.driven_of(function, {}).items():
                capability = graph.capabilities.get(fixture_id)
                if capability is None or capability.is_smoke:
                    continue
                if rgb_white(capability, written) or detent_white(capability, written):
                    names.add(capability.fixture.name)
        elif kind == "RGBMatrix":
            argb = matrix_colour(function)
            if argb is None or rgb_from_argb(argb) != WHITE:
                continue
            for fixture_id, written in graph.driven_of(function, groups).items():
                capability = graph.capabilities.get(fixture_id)
                if capability is not None and written:
                    names.add(capability.fixture.name)
    return names
