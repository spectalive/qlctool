"""Latched picks and stopped hooks for one semantic family frame."""

from lxml import etree

from .family_frames import _family_frame_handoff
from .show_graph import ShowGraph


def family_frame_picks(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    states: set[int],
    widget: etree._Element | None,
) -> tuple[tuple[int, frozenset[int]], ...]:
    """Latched picks and the state hooks their SoloFrame stops for each pick."""
    handoff = _family_frame_handoff(graph, groups, states, widget)
    if handoff is None:
        return ()
    _, toggles, hooks, _, _ = handoff
    stopped = frozenset(hooks)
    return tuple((function_id, stopped) for function_id in sorted(set(toggles) - hooks))
