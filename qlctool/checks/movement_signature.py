"""Everything the room can see of the movement a function starts, on the rigged heads.

Two buttons are the same button, to the room, when every EFX they start draws
the same figure - algorithm, size, centre, rotation, propagation, speed - and
moves every visible head the same way round from the same point of it. Spares
in a flight case are left out: what they do is seen by nobody (en-sala DMX
audit, 2026-09-26, where the seven `Alternado` buttons differed from the
defaults only on the spares).
"""

from lxml import etree

from .efx_rigged_heads import Head, efx_rigged_heads
from .show_graph import ShowGraph

# One EFX as the room sees it: its figure's settings and its rigged heads.
Figure = tuple[tuple[bytes, ...], tuple[Head, ...]]


def movement_signature(graph: ShowGraph, function_id: int, rigged: set[int]) -> frozenset[Figure]:
    """Every EFX `function_id` can start, as it moves the `rigged` heads."""
    figures: set[Figure] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or function.attrib.get("Type") != "EFX":
            continue
        heads = efx_rigged_heads(function, rigged)
        if not heads:
            continue
        settings = tuple(
            etree.tostring(child, with_tail=False)
            for child in function
            if isinstance(child.tag, str) and not child.tag.endswith("Fixture")
        )
        figures.add((settings, heads))
    return frozenset(figures)
