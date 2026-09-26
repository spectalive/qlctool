"""The latched picks of the SoloFrames that hand over the heads' position."""

from lxml import etree

from .family_frames import family_frame_handoff
from .show_graph import ShowGraph


def position_frame_picks(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    frame: etree._Element,
) -> tuple[tuple[int, frozenset[int]], ...]:
    """Each pick of a position family frame, with the state hooks it stops."""
    handoff = family_frame_handoff(graph, groups, states, frame)
    if handoff is None or "position" not in handoff[3]:
        return ()
    _, toggles, hooks, _, _ = handoff
    stopped = frozenset(hooks)
    return tuple((function_id, stopped) for function_id in sorted(set(toggles) - hooks))
