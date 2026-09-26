"""The fixtures a held scene recolours, when colour is all it does.

A bank button is a pure colour takeover: every fixture with red, green and
blue it writes gets a whole colour (`fixture_colour`), and it opens no dimmer.
A hit or a flash raises intensity and a strobe states no colour; those are
something else, and None is returned for them. Colour count is not the
question - a split recolours as much of the room as a solid.
"""

from lxml import etree

from .. import roles
from .fixture_colour import fixture_colour
from .show_graph import ShowGraph

RGB = (roles.RED, roles.GREEN, roles.BLUE)


def colour_takeover_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], scene: etree._Element
) -> set[int] | None:
    recoloured: set[int] = set()
    for fixture_id, written in graph.driven_of(scene, groups).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        if any(o in written for o in capability.offsets_for_role(roles.DIMMER)):
            return None
        if not any(o in written for role in RGB for o in capability.offsets_for_role(role)):
            continue
        if fixture_colour(graph, fixture_id, written) is None:
            return None
        recoloured.add(fixture_id)
    return recoloured or None
