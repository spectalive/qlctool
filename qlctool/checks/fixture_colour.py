"""The (r, g, b) a scene puts on one RGB fixture, with its white share folded back in.

A MAC WASH has a white emitter, so `rgbw_split` hands it a pastel red as R115
W140; a bar without one gets the same pastel as R255 G140 B140. The room sees
one colour, and a rule that compares colours has to see one too. None when
the fixture has no RGB or the scene leaves any of the three unwritten - a
colour claim is all three channels or nothing.
"""

from collections.abc import Mapping

from .. import roles
from .show_graph import ShowGraph

RGB = (roles.RED, roles.GREEN, roles.BLUE)
FULL = 255


def fixture_colour(
    graph: ShowGraph, fixture_id: int, written: Mapping[int, int | None]
) -> tuple[int, int, int] | None:
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return None
    stated: list[int] = []
    for role in RGB:
        values = [
            value
            for offset in capability.offsets_for_role(role)
            if (value := written.get(offset)) is not None
        ]
        if not values:
            return None
        stated.append(max(values))
    whites = [
        value
        for offset in capability.offsets_for_role(roles.WHITE)
        if (value := written.get(offset)) is not None
    ]
    white = max(whites) if whites else 0
    red, green, blue = stated
    # The full white of a fixture with a white emitter runs all four LED
    # (`rgbw_split` keeps r = g = b whole), so folding the white back in must
    # saturate rather than overflow.
    return (min(FULL, red + white), min(FULL, green + white), min(FULL, blue + white))
