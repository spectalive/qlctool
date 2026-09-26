"""What colour a Scene puts on which RGB channel: the items a colour signature is made of."""

from lxml import etree

from .. import roles
from .show_graph import ShowGraph


def scene_colours(graph: ShowGraph, function: etree._Element) -> set[tuple[object, ...]]:
    items: set[tuple[object, ...]] = set()
    for fixture_id, pairs in graph.driven_of(function, {}).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None:
            continue
        rgb = {
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE)
            for offset in capability.offsets_for_role(role)
        }
        items |= {
            (fixture_id, offset, value)
            for offset, value in pairs.items()
            if offset in rgb and value
        }
    return items
