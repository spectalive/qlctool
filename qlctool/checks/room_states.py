"""Which buttons replace the room's state, and which ones add to it.

A console is not a flat list of functions. This one is built around a solo
frame: the room is in exactly one of AUTO, the four moments, the work light or
the blackout, and everything else on the console rides on top of whatever that
is. Checking a button on its own would ask the wrong question - a matrix on
page 3 has no business opening a dimmer, because the state running underneath
it already did.

The frame is found by what its buttons *do*, never by their names. Several solo
frames hold a dozen buttons; only one holds buttons that between them drive the
whole rig, because that is what being the room's state means. A frame of a
hundred matrix looks, each painting one group, is not that however many
buttons it has.
"""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from ..localname import localname
from .function_of import function_of
from .reach import reach
from .show_graph import ShowGraph
from .startup_function import startup_function

# A state frame drives at least this share of the rig between its buttons.
WHOLE_RIG = 0.75


def room_states(
    root: etree._Element, graph: ShowGraph, groups: dict[int, tuple[int, ...]]
) -> set[int]:
    """The function ids that are mutually exclusive states of the room."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return set()
    lightable = {
        fixture_id
        for fixture_id, capability in graph.capabilities.items()
        if not capability.is_smoke
    }
    if not lightable:
        return set()

    startup = startup_function(root)
    best: set[int] = set()
    best_reach = 0
    for frame in iter_local(console, "SoloFrame"):
        inside = {
            function_id
            for button in frame
            if localname(button) == "Button" and (function_id := function_of(button)) is not None
        }
        if len(inside) < 2:
            continue
        if startup is not None and startup in inside:
            return inside
        touched = {
            fixture_id for function_id in inside for fixture_id in reach(graph, groups, function_id)
        } & lightable
        if len(touched) > best_reach:
            best, best_reach = inside, len(touched)
    return best if best_reach >= len(lightable) * WHOLE_RIG else set()
