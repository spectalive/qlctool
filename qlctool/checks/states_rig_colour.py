"""Whether a scene states a colour on the rig, not only on the smoke columns.

`Flash Color` is the strobe over whatever colour is running: it writes no
colour on any fixture of the rig, only dimmers and strobe channels, and lights
the vertical smoke columns white beside it. The owner ruled those columns stay
white and steady there ("Flash Color: white, not strobing", 2026-09-26; ruling
D3), while every flash that states a colour of its own - `Flash 100%`'s white,
a colour hit - strobes them like any other fixture. This is the structural line
between the two, read off the roles a scene writes, never off its name.
"""

from collections.abc import Mapping

from .color_roles import COLOUR
from .show_graph import ShowGraph


def states_rig_colour(graph: ShowGraph, written: Mapping[int, Mapping[int, int | None]]) -> bool:
    """True when the scene writes a colour channel of some fixture that is not smoke."""
    for fixture_id, pairs in written.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        colour = {offset for role in COLOUR for offset in capability.offsets_for_role(role)}
        if colour & set(pairs):
            return True
    return False
