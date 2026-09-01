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

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, findall_local, iter_local, localname
from .show_graph import ShowGraph, reach

# A state frame drives at least this share of the rig between its buttons.
WHOLE_RIG = 0.75


def room_states(root: etree._Element, graph: ShowGraph, groups) -> set[int]:
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

    startup = _startup_function(root)
    best: set[int] = set()
    best_reach = 0
    for frame in iter_local(console, "SoloFrame"):
        inside = {
            function_id
            for button in frame
            if localname(button) == "Button" and (function_id := _function_of(button)) is not None
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


def _function_of(button: etree._Element) -> int | None:
    function = find_local(button, "Function")
    if function is None:
        return None
    function_id = int(function.attrib.get("ID", NO_FUNCTION))
    return None if function_id == NO_FUNCTION else function_id


def _startup_function(root: etree._Element) -> int | None:
    for element in findall_local(root, "Engine"):
        startup = find_local(element, "Autostart")
        if startup is not None and startup.text and startup.text.isdigit():
            return int(startup.text)
    return None
