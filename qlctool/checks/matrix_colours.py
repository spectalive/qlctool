"""What colour an RGBMatrix paints on which fixture of its group: signature items."""

from lxml import etree

from .. import roles
from ..xmlutil import find_local
from .matrix_colour import matrix_colour
from .show_graph import ShowGraph


def matrix_colours(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function: etree._Element
) -> set[tuple[object, ...]]:
    group = find_local(function, "FixtureGroup")
    colour = matrix_colour(function)
    text = (group.text or "") if group is not None else ""
    if not text.isdigit() or colour is None:
        return set()
    return {
        (fixture_id, "matrix", colour)
        for fixture_id in groups.get(int(text), ())
        if (capability := graph.capabilities.get(fixture_id)) is not None
        and any(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    }
